#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font

ev3 = EV3Brick()
ev3.screen.set_font(Font())
color_sensor = ColorSensor(Port.S1)

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

draw_board("| | | | | | | | |\n| | | | | | | | |\n| | | | | | | | |\n| | | |B|W| | | |\n| | | |W|W|W| | |\n| | | | | | | | |\n| | | | | | | | |\n| | | | | | | | |\n")
wait(1000000)