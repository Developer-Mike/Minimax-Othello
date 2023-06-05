# Compile core.cpp
print("Compiling...")
import cppyy
cppyy.cppdef(open("core.cpp").read())
import cppyy.gbl as core
print("Compiled.")

import json

MINIMAX_DEPTH = 7
board = core.Board()

# Utility function to convert a move to a dict
def move_to_dict(move: core.Move) -> dict:
    return {
        "x": move.placedTile.x, 
        "y": move.placedTile.y, 
        "flipped": [
            {"x": flipped.x, "y": flipped.y} for flipped in move.flippedTiles
        ]
    }

# Start a new game with a fresh board
def start(json: dict):
    global board

    board = core.Board()
    return {
        "success": True,
        "board": str(board.toString()),
        "isBlackTurn": board.isBlackTurn
    }

# Get the current board
def get_board(json: dict):
    return {
        "success": True,
        "board": str(board.toString()),
        "isBlackTurn": board.isBlackTurn,
        "scoreBlack": board.evaluateScore()
    }

# Register a move on the board (made by the player)
def register_move(json: dict):
    x = int(json["x"])
    y = int(json["y"])

    move = core.Move(core.TilePosition(x, y), [])
    board.setFlippedTiles(move)

    # Validate move
    if board.array[y][x] != " ":
        return {
            "success": False,
            "message": "Invalid move. Field is not empty."
        }
    elif len(move.flippedTiles) == 0:
        return {
            "success": False,
            "message": "Invalid move. No tiles get flipped."
        }

    # Register move
    board.makeMove(move)
    return {
        "success": True,
        "board": str(board.toString())
    }

# Get all possible moves for the current player
def get_moves(json: dict):
    return {
        "success": True,
        "moves": [move_to_dict(move) for move in board.getPossibleMoves()]
    }

# Let the AI make a move
def ai_move(json: dict):
    move = core.getBestMove(board, MINIMAX_DEPTH)
    board.makeMove(move)
    
    return {
        "success": True,
        "move": move_to_dict(move),
        "board": str(board.toString())
    }

# Map shared keys to functions
from shared import Functions
FUNCTIONS_MAP = {
    Functions.START: start,
    Functions.GET_BOARD: get_board,
    Functions.REGISTER_MOVE: register_move,
    Functions.GET_MOVES: get_moves,
    Functions.AI_MOVE: ai_move
}

# Listen for connection requests from the EV3
import socket
s = None
client = None

def listen():
    global s, client

    # Create socket and bind to port 3000
    s = socket.socket()
    ip = socket.gethostbyname(socket.gethostname())
    s.bind((ip, 3000))

    # Listen for connection
    print("Listening on", ip)
    s.listen(1)

    # Accept connection
    client, address = s.accept()
    print("Connected to", address)

# Main loop
if __name__ == "__main__":
    while True:
        # If no client is connected, listen for a connection
        if client is None:
            listen()

        try:
            # Receive data and parse it as JSON to a dict
            data = client.recv(1024).decode("utf-8")
            data = json.loads(data)

            print("Received:", data)

            # Find the function to execute
            requested_function = FUNCTIONS_MAP.get(data["function"])
            if requested_function is not None:
                # Execute the function and send the response back to the EV3
                response = requested_function(data["parameters"])
                client.send(bytes(json.dumps(response), "utf-8"))
            else:
                print("Unknown function:", data)
        except:
            client = None
            print("Connection lost.")