#!/usr/bin/python
import threading

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program, utils
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle
import logging

levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL)
logging.basicConfig(format='%(asctime)-15s [%(levelname)] [%(name)-12s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('PICKUP PRODUCT')

OBJECT_POSITION = [1450, -200, -100]
PERIOD = 10

def periodic_main():
    # Add Connection to the calibration channel
    logger.info('Demonstrator Programm Api using pika version: %s' % pika.__version__)

    # Send the program for calibration
    demonstrator_program = Program()
    if demonstrator_program.connect(): ## Demonstrator is connected
        demonstrator_program.reset()
        demonstrator_program.append_all_instructions(utils.pick_object(object_position=OBJECT_POSITION,
                                                                       final_destination=PRODUCT_POSITION_CAMERA,
                                                                       retain=False)
                                                     )

        ## Execute
        demonstrator_program.execute()
        threading.Timer(PERIOD, periodic_main).start()
    else:
        logger.error('Connection cannot be established to the Demonstrator')


if __name__ == '__main__':
    periodic_main()
