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
    [1747.50, -220.30, -243.0]
]

PLACE_POINTS = [
    [963.20, -217.30, -243.0],
]


def periodic_main():
    demonstrator_program = Program()
    if demonstrator_program.connect(): ## Demonstrator is connected
        demonstrator_program.reset()

        # execute Pick and place
        for i in range(1):
            demonstrator_program.append_all_instructions(
                utils.pick_and_place_object_reverse(object_position=PICK_POINTS[i], place_destination=PLACE_POINTS[i]))

        # # wait for 5 seconds
        demonstrator_program.append_all_instructions(
            utils.wait(2000.0))

        # execute place & pick
        for i in range(1):
            demonstrator_program.append_all_instructions(
                 utils.pick_and_place_object_reverse(object_position=PLACE_POINTS[i], place_destination=PICK_POINTS[i]))

        ## Execute
        demonstrator_program.execute()
        threading.Timer(30, periodic_main).start()

    else:
        print('Connection cannot be established to the Demonstrator')


if __name__ == '__main__':
    periodic_main()
