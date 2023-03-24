#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

ev3 = EV3Brick()
color_sensor = ColorSensor(Port.S1)

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

