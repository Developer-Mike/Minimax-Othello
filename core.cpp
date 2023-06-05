#include <iostream>
#include <algorithm>
#include <string>
#include <list>
#include <array>
#include <limits>
#include <thread>
#include <chrono>

#define INF numeric_limits<int>::max()
#define EMPTY ' '
#define BLACK 'B'
#define WHITE 'W'

using namespace std;

// Struct for a position on the board
struct TilePosition {
    int x = -1;
    int y = -1;

    bool operator==(const TilePosition& other) const {
        return x == other.x && y == other.y;
    }

    string toString() {
        return "(" + to_string(x) + ":" + to_string(y) + ")";
    }
};

// Struct for a move
struct Move {
    TilePosition placedTile;
    list<TilePosition> flippedTiles;

    bool operator==(const Move& other) const {
        return placedTile.x == other.placedTile.x && placedTile.y == other.placedTile.y;
    }

    string toString() {
        return "Placed tile " + placedTile.toString() + " and rotating " + to_string(flippedTiles.size()) + " tiles.";
    }
};

// Struct for the game board
struct Board {
    // 2D array for the board
    array<array<char, 8>, 8> array = {{
        {EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, BLACK, WHITE, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, WHITE, BLACK, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY},
        {EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY}
    }};
    bool isBlackTurn = false;

    // Update the flipped tiles for a move
    void setFlippedTiles(Move* move) {
        // Get adjacent tiles
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                if (x == 0 && y == 0) continue;

                int newX = move->placedTile.x + x;
                int newY = move->placedTile.y + y;

                if (newX < 0 || newX >= 8 || newY < 0 || newY >= 8) continue; // Out of bounds
                if (array[newY][newX] == (isBlackTurn ? BLACK : WHITE) || array[newY][newX] == EMPTY) continue; // Not a tile to flip

                /* DEBUG
                Board newBoard(*this);
                newBoard.array[move->placedTile.x][move->placedTile.y] = 'H';
                cout << newBoard.toString() << endl; 
                */
                
                // While the tile is not empty and not the same color as the placed tile
                list<TilePosition> tilesToFlip;
                while (true) {
                    if (array[newY][newX] == (isBlackTurn ? WHITE : BLACK)) {
                        tilesToFlip.push_back({newX, newY});
                    } else if (array[newY][newX] == (isBlackTurn ? BLACK : WHITE)) {
                        // Tiles are sourrounded by the same color -> Valid move
                        move->flippedTiles.splice(move->flippedTiles.end(), tilesToFlip);
                        break;
                    } else break; // Invalid move

                    // Check next tile in the same direction
                    newX += x;
                    newY += y;
                    if (newX < 0 || newX >= 8 || newY < 0 || newY >= 8) break;
                }
            }
        }

        // Remove duplicates
        move->flippedTiles.unique();
    }

    list<Move> getPossibleMoves() {
        list<Move> moves;

        // For each field
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                char tile = array[i][j];
                if (tile != (isBlackTurn ? WHITE : BLACK)) continue; // Not a valid tile

                // Get adjacent tiles
                for (int x = -1; x <= 1; x++) {
                    for (int y = -1; y <= 1; y++) {
                        int newX = i + x;
                        int newY = j + y;

                        if (newX < 0 || newX >= 8 || newY < 0 || newY >= 8) continue;
                        if (array[newY][newX] != EMPTY) continue;

                        // Add to list
                        moves.push_back({{newX, newY}, {}});
                    }
                }
            }
        }
        
        // Remove duplicates
        //TODO: moves.sort();
        moves.unique();

        /* DEBUG 
        Board newBoard(*this);
        for (Move move : moves) newBoard.array[move.placedTile.x][move.placedTile.y] = 'H';
        cout << newBoard.toString() << endl;
        */

        // Remove tiles that don't flip any tiles
        for (auto it = moves.begin(); it != moves.end();) {
            // Update flipped tiles
            setFlippedTiles(&*it);

            if (it->flippedTiles.size() == 0) it = moves.erase(it);
            else it++;
        }

        return moves;
    }

    // Make a move
    void makeMove(Move* move) {
        if (move->placedTile.x != -1 && move->placedTile.y != -1) {
            // Place new tile
            array[move->placedTile.y][move->placedTile.x] = isBlackTurn ? BLACK : WHITE;

            // Flip tiles
            for (TilePosition tilePosition : move->flippedTiles) {
                array[tilePosition.y][tilePosition.x] = isBlackTurn ? BLACK : WHITE;
            }
        }

        // Switch turn
        isBlackTurn = !isBlackTurn;
    }

    // Evaluate the score for the current board
    // White is maximizing player
    int evaluateScore() {
        int score = 0;

        // For each field
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                // If the tile is the same color as the player, add to score (positive), else subtract (negative)
                if (array[i][j] == BLACK) {
                    score--;
                } else if (array[i][j] == WHITE) {
                    score++;
                }
            }
        }

        return score;
    }

    string toString() {
        string result;

        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                result += "|";
                result += array[i][j];
            }
            result += "|\n";
        }
        
        return result;
    }
};

// Minimax algorithm based on https://www.geeksforgeeks.org/minimax-algorithm-in-game-theory-set-4-alpha-beta-pruning/
int _minimax(Board* board, int depth, int alpha = -INF, int beta = INF) {
    // If depth is reached return the score
    if (depth == 0) return board->evaluateScore();

    list<Move> moves = board->getPossibleMoves();
    // If no moves are possible, game is over and return the score
    if (moves.size() == 0) {
        board->isBlackTurn = !board->isBlackTurn;
        moves = board->getPossibleMoves();

        if (moves.size() == 0) return board->evaluateScore();
    }

    if (!board->isBlackTurn) {
        int maxEval = -INF;
        for (Move move : moves) {
            Board newBoard(*board);
            newBoard.makeMove(&move);

            // Recursively call minimax and get the best possible score
            int eval = _minimax(&newBoard, depth - 1, alpha, beta);
            
            // Alpha-beta pruning
            maxEval = max(maxEval, eval);
            alpha = max(alpha, maxEval);
            if (beta <= alpha) break;
        }

        return maxEval;
    } else {
        int maxEval = INF;
        for (Move move : moves) {
            Board newBoard(*board);
            newBoard.makeMove(&move);

            // Recursively call minimax and get the best possible score
            int eval = _minimax(&newBoard, depth - 1, alpha, beta);
            
            // Alpha-beta pruning
            maxEval = min(maxEval, eval);
            beta = min(beta, maxEval);
            if (beta <= alpha) break;
        }

        return maxEval;
    }
}

void _launchMinimax(Board board, Move move, int depth, bool isMaximizingPlayer, int &bestEval, Move &bestMove, int &progress, int total) {
    chrono::steady_clock::time_point start = chrono::steady_clock::now();

    // Make move
    Board newBoard(board);
    newBoard.makeMove(&move);

    // Minimax and if best move yet, update best move
    int eval = _minimax(&newBoard, depth);
    if ((isMaximizingPlayer && eval > bestEval) || (!isMaximizingPlayer && eval < bestEval)) {
        bestEval = eval;
        bestMove = move;
    }

    // Update debug info
    progress++;
    long duration = chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - start).count();
    cout << "Processed " << progress << "/" << total << " solutions (" << duration << "ms" << "). \r";
}

// Function to get the best move using minimax
Move getBestMove(Board* board, int depth) {
    list<Move> possibleMoves = board->getPossibleMoves();
    list<thread> threads;

    bool isMaximizingPlayer = !board->isBlackTurn;

    int progress = 0;
    int bestEval = isMaximizingPlayer ? -INF : INF;
    Move bestMove;

    // Launch thread for each possible move
    for (Move move : possibleMoves) {
        threads.push_back(thread(_launchMinimax, *board, move, depth, isMaximizingPlayer, ref(bestEval), ref(bestMove), ref(progress), possibleMoves.size()));
    }
    // Wait for all threads to finish
    for (thread &thread : threads) thread.join();

    cout << endl << "Best eval: " << bestEval << endl;
    return bestMove;
}

// For testing
int main() {
    Board board;
    Move move;

    long total = 0;
    long max = 0;
    int count = 0;

    int no_possible_move_count = 0;
    while (no_possible_move_count < 2) {
        chrono::steady_clock::time_point start = chrono::steady_clock::now();

        move = getBestMove(&board, 6);
        cout << move.toString() << endl;

        long duration = chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - start).count();
        if (duration > max) max = duration;
        total += duration;
        count++;

        board.makeMove(&move);
        cout << board.toString() << endl;

        if (move.placedTile.x == -1) no_possible_move_count++;
        else no_possible_move_count = 0;
    }

    cout << "Average: " << to_string(total / count) << "ms" << endl;
    cout << "Max: " << to_string(max) << "ms" << endl;

    int score = board.evaluateScore();
    if (score > 0) cout << "White wins! (" + to_string(score) + ")" << endl;
    else if (score < 0) cout << "Black wins! (" + to_string(score) + ")" << endl;
    else cout << "Draw!" << endl;

    return 0;
}