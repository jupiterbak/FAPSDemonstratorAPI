#!/usr/bin/python
import threading

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program, utils
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle

PICK_POINTS = [
    [1830.0, 185.0, -100.0],
    [1425.6, 185.0, -100.0],
    [984.6, 182.4, -100.0]
]

PLACE_POINTS = [
    [1340, -78, -100.0],
    [1340, -230, -100.0],
    [1494, -78, -100.0]
]


def periodic_main():
    demonstrator_program = Program()
    if demonstrator_program.connect(): ## Demonstrator is connected
        demonstrator_program.reset()

        # execute Pick and place
        for i in range(3):
            demonstrator_program.append_all_instructions(
                utils.pick_and_place_object(object_position=PICK_POINTS[i], place_destination=PLACE_POINTS[i]))

        # # wait for 5 seconds
        demonstrator_program.append_all_instructions(
            utils.wait(2000.0))

        # execute place & pick
        for i in range(3):
            demonstrator_program.append_all_instructions(
                 utils.pick_and_place_object(object_position=PLACE_POINTS[i], place_destination=PICK_POINTS[i]))

        ## Execute
        demonstrator_program.execute()
        threading.Timer(46, periodic_main).start()

    else:
        print('Connection cannot be established to the Demonstrator')


if __name__ == '__main__':
    periodic_main()
