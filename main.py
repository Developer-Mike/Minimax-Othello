#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font

IP_ADDRESS = "192.168.178.112"
from shared import Functions
from client import Client
client = Client(IP_ADDRESS, 3000)

ev3 = EV3Brick()
ev3.screen.set_font(Font())
color_sensor = None #ColorSensor(Port.S1)

AI_IS_WHITE = True

def no_move(move: dict) -> bool:
    return move["x"] == -1 and move["y"] == -1

def draw_board(board: str):
    ev3.screen.clear()
    splitted_board = board.split("\n")

    for y in range(len(splitted_board)):
        for x in range(len(splitted_board[y])):
            draw_x = x * 8
            draw_y = y * 16

            if splitted_board[y][x].isalpha():
                draw_x -= 4

            ev3.screen.draw_text(draw_x, draw_y, splitted_board[y][x])
        ev3.screen.draw_text(3, y * 16 + 3, "_" * 18)

def draw_state_text(text: str):
    ev3.screen.draw_box(130, 0, 177, 128, color=Color.WHITE, fill=True)

    FRAGMENT_LENGTH = 7
    for i, text_fragment in enumerate([text[i:i + FRAGMENT_LENGTH] for i in range(0, len(text), FRAGMENT_LENGTH)]): 
        ev3.screen.draw_text(132, i * 8, text_fragment.strip())

def move_to_field(x: int, y: int, move_home: bool = False):
    if move_home: move_to_home()
    pass

def move_to_home():
    pass

def flip(x: int, y: int):
    if x is not None and y is not None:
        move_to_field(x, y, move_home=True)
    pass

def scan(x: int, y: int) -> Color:
    if x is not None and y is not None:
        move_to_field(x, y, move_home=True)
    
    return color_sensor.color()

# Restore board
board = client.execute(Functions.GET_BOARD)
draw_board(board["board"])
is_black_turn = board["isBlackTurn"]

while True:
    invalid_move_count = 0
    while invalid_move_count < 2:
        if not is_black_turn and AI_IS_WHITE:
            draw_state_text("AI is thinking...")
            # AI move
            response = client.execute(Functions.AI_MOVE)

            # Check if AI could not find a move
            if no_move(response["move"]):
                print("AI could not find a move. Skipping turn.")
                invalid_move_count += 1
                is_black_turn = not is_black_turn
                continue
            else:
                invalid_move_count = 0

            # Update board
            draw_board(response["board"])
        else:
            # Get possible moves
            response = client.execute(Functions.GET_MOVES)
            if len(response["moves"]) == 0:
                print("No moves available. Skipping turn.")
                invalid_move_count += 1
                is_black_turn = not is_black_turn
                continue
            else:
                invalid_move_count = 0

            # Wait for button press
            draw_state_text("Waiting for player...")
            while Button.CENTER not in ev3.buttons.pressed():
                wait(100)

            # TODO: Scan field
            client.execute(Functions.AI_MOVE)
            draw_board(response["board"])
        
        is_black_turn = not is_black_turn

    # Game over
    response = client.execute(Functions.GET_BOARD)
    score_black = response["scoreBlack"]

    text = ""
    if score_black == 0: text = "Draw!"
    elif score_black > 0: text = "Black won with {0} tiles more!".format(score_black)
    else: text = "White won with {0} tiles more!".format(-score_black)
    draw_state_text(text)

    # Wait for button press
    while Button.CENTER not in ev3.buttons.pressed():
        wait(100)

    # Restart game
    response = client.execute(Functions.START)
    draw_board(response["board"])
    is_black_turn = response["isBlackTurn"]