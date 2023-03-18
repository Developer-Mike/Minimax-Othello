#include <iostream>
#include <algorithm>
#include <string>
#include <list>
#include <array>
#include <set>
#include <limits>
#include <cmath>
#include <thread>
#include <chrono>

#define INF numeric_limits<int>::max()
#define EMPTY ' '
#define BLACK 'B'
#define WHITE 'W'

using namespace std;

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

struct Board {
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

    void setFlippedTiles(Move* move) {
        for (int x = -1; x <= 1; x++) {
            for (int y = -1; y <= 1; y++) {
                if (x == 0 && y == 0) continue;

                int newX = move->placedTile.x + x;
                int newY = move->placedTile.y + y;

                if (newX < 0 || newX >= 8 || newY < 0 || newY >= 8) continue;
                if (array[newX][newY] == (isBlackTurn ? BLACK : WHITE) || array[newX][newY] == EMPTY) continue;

                /* DEBUG
                Board newBoard(*this);
                newBoard.array[move->placedTile.x][move->placedTile.y] = 'H';
                cout << newBoard.toString() << endl; 
                */
                
                list<TilePosition> tilesToFlip;
                while (true) {
                    if (array[newX][newY] == (isBlackTurn ? WHITE : BLACK)) {
                        tilesToFlip.push_back({newX, newY});
                    } else if (array[newX][newY] == (isBlackTurn ? BLACK : WHITE)) {
                        move->flippedTiles.splice(move->flippedTiles.end(), tilesToFlip);
                        break;
                    } else break;

                    newX += x;
                    newY += y;
                    if (newX < 0 || newX >= 8 || newY < 0 || newY >= 8) break;
                }
            }
        }

        move->flippedTiles.unique();
    }

    list<Move> getPossibleMoves() {
        list<Move> moves;

        // Get all tiles that can be placed
        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                char tile = array[i][j];
                if (tile != (isBlackTurn ? WHITE : BLACK)) continue;

                // Get adjacent tiles
                for (int x = -1; x <= 1; x++) {
                    for (int y = -1; y <= 1; y++) {
                        if (x == 0 && y == 0) continue;

                        int newX = i + x;
                        int newY = j + y;

                        if (newX < 0 || newX >= 8 || newY < 0 || newY >= 8) continue;
                        if (array[newX][newY] != EMPTY) continue;

                        moves.push_back({{newX, newY}, {}});
                    }
                }
            }
        }
        
        // Remove duplicates
        moves.unique();

        /* DEBUG
        Board newBoard(*this);
        for (Move move : moves) newBoard.array[move.placedTile.x][move.placedTile.y] = 'H';
        cout << newBoard.toString() << endl;
        */

        // Remove tiles that don't flip any tiles
        for (auto it = moves.begin(); it != moves.end();) {
            setFlippedTiles(&*it);

            if (it->flippedTiles.size() == 0) {
                it = moves.erase(it);
            } else {
                it++;
            }
        }

        return moves;
    }

    void makeMove(Move* move) {
        array[move->placedTile.x][move->placedTile.y] = isBlackTurn ? BLACK : WHITE;
        for (TilePosition tilePosition : move->flippedTiles) {
            array[tilePosition.x][tilePosition.y] = isBlackTurn ? BLACK : WHITE;
        }

        isBlackTurn = !isBlackTurn;
    }

    int evaluateScore(bool isBlack) {
        int score = 0;

        for (int i = 0; i < 8; i++) {
            for (int j = 0; j < 8; j++) {
                if (array[i][j] == (isBlack ? BLACK : WHITE)) {
                    score++;
                } else if (array[i][j] == (isBlack ? WHITE : BLACK)) {
                    score--;
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

int _minimax(Board* board, int depth, bool isBlack, bool forBlack, int alpha = -INF, int beta = INF) {
    if (depth == 0) return board->evaluateScore(forBlack);

    list<Move> moves = board->getPossibleMoves();
    if (moves.size() == 0) return board->evaluateScore(forBlack);

    int maxEval = -INF;
    for (Move move : moves) {
        Board newBoard(*board);
        newBoard.makeMove(&move);

        int eval = _minimax(&newBoard, depth - 1, !isBlack, forBlack, alpha, beta);
        maxEval = max(maxEval, eval);

        if (isBlack) alpha = max(alpha, maxEval);
        else beta = min(beta, -maxEval);

        if (beta <= alpha) break;
    }

    return maxEval;
}

void _launchMinimax(Board board, Move move, int depth, int &bestEval, Move &bestMove) {
    chrono::steady_clock::time_point start = chrono::steady_clock::now();

    Board newBoard(board);
    newBoard.makeMove(&move);

    int eval = _minimax(&newBoard, depth, board.isBlackTurn, board.isBlackTurn);
    if (eval > bestEval) {
        bestEval = eval;
        bestMove = move;
    }

    cout << chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - start).count() << "ms - ";
}

Move getBestMove(Board* board, int depth) {
    list<Move> possibleMoves = board->getPossibleMoves();
    list<thread> threads;

    int bestEval = -INF;
    Move bestMove;

    for (Move move : possibleMoves) {
        threads.push_back(thread(_launchMinimax, *board, move, depth, ref(bestEval), ref(bestMove)));
    }
    for (thread &thread : threads) thread.join();

    cout << endl << "Best eval: " << bestEval << endl;
    return bestMove;
}

int main() {
    Board board;
    Move move;

    do {
        move = getBestMove(&board, 6);
        cout << move.toString() << endl;

        board.makeMove(&move);
        cout << board.toString() << endl;
    } while (move.placedTile.x != -1);

    int score = board.evaluateScore(true);
    if (score > 0) cout << "Black wins! (" + to_string(score) + ")" << endl;
    else if (score < 0) cout << "White wins! (" + to_string(-score) + ")" << endl;
    else cout << "Draw!" << endl;

    return 0;
}