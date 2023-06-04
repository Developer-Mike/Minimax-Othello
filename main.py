#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font
from time import time

# Init connection to server
IP_ADDRESS = "192.168.178.112" # Change this to the IP address that gets printed in the terminal when you run server.py
from shared import Functions
from client import Client
client = Client(IP_ADDRESS, 3000)

# Constants
AI_IS_WHITE = True

MOVE_SPEED = (500, 500)
LIFT_SPEED = 200
FIELD_SIZE = (110, 210)
MAX_DURATION = 5000 # Avoid stalls with max time for move
MAX_STALLS = 5 # Avoid stalls with max stalls for move
current_location = [0, 0]

ev3 = EV3Brick()
ev3.screen.set_font(Font())

# Init Motors
motor_lift = Motor(Port.A)
motor_x = Motor(Port.B)
motor_y = Motor(Port.C)
color_sensor = ColorSensor(Port.S1)

#region Movement
def move_home():
    global current_location

    # Move to home with stall detection
    motor_x.run_until_stalled(-100000, duty_limit=50)
    motor_y.run_until_stalled(-100000, duty_limit=30)

    # Reset location
    current_location = [0, 0]

def move_to(target_x: int, target_y: int, align_sensor: bool = False, home_first: bool = False):
    global current_location
    if home_first: move_home()
    if align_sensor: target_y += 1 # Sensor has a y offset of 1

    # Allow movement asynchroniously
    motor_x.run_angle(MOVE_SPEED[0], (FIELD_SIZE[0] * (target_x - current_location[0])), wait=False)
    motor_y.run_angle(MOVE_SPEED[1], (FIELD_SIZE[1] * (target_y - current_location[1])), wait=False)

    # Wait for movement to finish
    passed_ms = 0
    not_moved_since = 0
    while not_moved_since < MAX_STALLS and passed_ms < MAX_DURATION:
        # Count stalls
        if motor_x.speed() == 0 and motor_y.speed() == 0:
            not_moved_since += 1
        else: not_moved_since = 0

        wait(50)
        passed_ms += 50

    # Update current location
    current_location = [target_x, target_y]
    print("Movement took: " + str(passed_ms) + "ms")

def take_new_piece():
    global current_location
    origin_pos = current_location

    # Make sure the lift_motor is at the top
    drop_piece()
    # Move to new piece dispenser
    move_to(0, 8)
    # Lift piece
    lift_piece(new_piece_lift = True)
    # Move back to old position
    move_to(origin_pos[0], origin_pos[1])

def lift_piece(new_piece_lift: bool = False):
    # Lower pickup magnet
    if not new_piece_lift: 
        motor_lift.run_target(LIFT_SPEED, -450)
    else:
        # The new piece dispenser is a bit higher, so we need to lower the magnet a bit less
        motor_lift.run_target(LIFT_SPEED, -300)
        
    # Lift piece
    motor_lift.run_target(LIFT_SPEED, -175)

def drop_piece():
    # Lift magnet and detach piece
    motor_lift.run_until_stalled(LIFT_SPEED, duty_limit=0.1)
    motor_lift.reset_angle(0)

def has_piece() -> bool:
    return True # TODO: Implement
#endregion

#region Logic
def find_made_move(possible_moves: list) -> dict:
    # For each possible move
    for possible_move in possible_moves:
        # Move to field
        move_to(possible_move["x"], possible_move["y"], align_sensor=True)
        # Check if field contains a piece
        if has_piece():
            return possible_move
    else:
        return None
#endregion

#region Debug
def draw_board(board: str):
    ev3.screen.clear()
    splitted_board = board.split("\n")

    # Loop through board and draw each character (aligned in a grid)
    for y in range(len(splitted_board)):
        for x in range(len(splitted_board[y])):
            draw_x = x * 8
            draw_y = y * 16

            if splitted_board[y][x].isalpha():
                draw_x -= 4

            ev3.screen.draw_text(draw_x, draw_y, splitted_board[y][x])
        ev3.screen.draw_text(3, y * 16 + 3, "_" * 18)

def draw_state_text(text: str):
    # Clear state text
    ev3.screen.draw_box(130, 0, 177, 128, color=Color.WHITE, fill=True)

    # Draw new state text (split into multiple lines)
    LINE_LENGTH = 7
    for i, text_fragment in enumerate([text[i:i + LINE_LENGTH] for i in range(0, len(text), LINE_LENGTH)]): 
        ev3.screen.draw_text(132, i * 10, text_fragment.strip())
#endregion

# Init Position
drop_piece()
move_home()

# Init Game and Restore board
board = client.execute(Functions.GET_BOARD)
draw_board(board["board"])
is_black_turn = board["isBlackTurn"]

# Play forever
while True:
    invalid_move_count = 0
    # While either player can make a move
    while invalid_move_count < 2:
        # Check if ai should move
        if not is_black_turn and AI_IS_WHITE:
            draw_state_text("AI is thinking...")
            # AI move
            response = client.execute(Functions.AI_MOVE)

            # Check if AI could not find a move
            if response["move"]["x"] == -1 and response["move"]["y"] == -1:
                print("AI could not find a move. Skipping turn.")
                invalid_move_count += 1
                is_black_turn = not is_black_turn
                continue
            else:
                invalid_move_count = 0

            # Update debug board
            draw_board(response["board"])
        else:
            # Get possible moves and skip player turn if no moves are available
            response = client.execute(Functions.GET_MOVES)
            possible_moves = response["moves"]
            if len(possible_moves) == 0:
                print("No moves available. Skipping turn.")
                invalid_move_count += 1
                is_black_turn = not is_black_turn
                continue
            else:
                invalid_move_count = 0

            # Wait for button press (Wait until player places piece)
            draw_state_text("Waiting for player...")
            while Button.CENTER not in ev3.buttons.pressed():
                wait(100)

            made_move = find_made_move(possible_moves)
            if made_move is None:
                print("ERROR") # TODO: Handle error

            # Register move on server
            response = client.execute(Functions.REGISTER_MOVE, made_move)
            draw_board(response["board"])
        
        # Alternate turn
        is_black_turn = not is_black_turn

    # Game over
    # Get score
    response = client.execute(Functions.GET_BOARD)
    score_black = response["scoreBlack"]

    # Draw winner text
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