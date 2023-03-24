print("Compiling...")
import cppyy
cppyy.cppdef(open("core.cpp").read())
import cppyy.gbl as core
print("Compiled.")

board = core.Board()

def move_to_dict(move: core.Move) -> dict:
    return {
        "x": move.placedTile.x, 
        "y": move.placedTile.y, 
        "flipped": [
            {"x": flipped.x, "y": flipped.y} for flipped in move.flippedTiles
        ]
    }

import flask
from flask import request, jsonify

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/start', methods=['GET'])
def start():
    board = core.Board()
    return jsonify({"success": True})

# /register-move?x=1&y=2
@app.route('/register-move', methods=['GET'])
def make_move():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))

    move = core.Move(core.TilePosition(x, y), [])
    board.setFlippedTiles(move)

    if board.array[y][x] != " ":
        return jsonify({
            "success": False,
            "message": "Invalid move. Field is not empty."
        })
    elif len(move.flippedTiles) == 0:
        return jsonify({
            "success": False,
            "message": "Invalid move. No tiles get flipped."
        })

    board.makeMove(move)
    return jsonify({
        "success": True,
        "board": str(board.toString())
    })

@app.route('/get-moves', methods=['GET'])
def get_moves():
    return jsonify({
        "moves": [move_to_dict(move) for move in board.getPossibleMoves()]
    })

@app.route('/ai-move', methods=['GET'])
def ai_move():
    move = core.getBestMove(board, 6)
    return jsonify({
        "success": True,
        "move": move_to_dict(move)
    })

app.run()