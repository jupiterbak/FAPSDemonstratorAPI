#!/usr/bin/python
import threading

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program, utils
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle

PICK_POINTS = [2331.5, 182.4, -100.0]

PLACE_POINTS = [820.0, -255.0, 178.0]


def periodic_main():
    demonstrator_program = Program()
    if demonstrator_program.connect(): ## Demonstrator is connected
        demonstrator_program.reset()

        demonstrator_program.append_all_instructions(
            utils.pick_object(object_position=PICK_POINTS, retain=True, execute=False))

        demonstrator_program.append_all_instructions(
            utils.goto_position(x=PLACE_POINTS[0], y=PLACE_POINTS[1], z=PLACE_POINTS[2], positioning_mode="Absolute"))

        demonstrator_program.append_all_instructions(
            utils.wait(1000.0))

        demonstrator_program.append_all_instructions(
            utils.open_gripper())
        demonstrator_program.append_all_instructions(
            utils.wait(100.0))
        demonstrator_program.append_all_instructions(
            utils.close_gripper())

        # Execute
        demonstrator_program.execute()

    else:
        print('Connection cannot be established to the Demonstrator')


if __name__ == '__main__':
    periodic_main()
