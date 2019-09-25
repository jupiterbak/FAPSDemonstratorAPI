#!/usr/bin/python

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle


if __name__ == '__main__':
    demonstrator_program = Program()
    if demonstrator_program.connect():
                demonstrator_program.reset()
                # set the velocity to 20%
                demonstrator_program.append_instruction(
                    Command.CMD_SET_PATH_VELO,
                    CommandMode.WCD,
                    20,
                    0,
                    0,
                    ParameterMode.ABSOLUTE,
                    0
                )
                # Goto to camera position
                demonstrator_program.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, 0,
                                                 PT_PRODUCT_CAMERA, 0, ParameterMode.ABSOLUTE, 0)
                # Wait until movement is finished
                demonstrator_program.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                                 ParameterMode.ABSOLUTE, 0)
                # Take a picture
                demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC, 1, 0,
                                                 ParameterMode.ABSOLUTE, 0)
                # Wait for 1000 ms
                demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                 ParameterMode.ABSOLUTE, 1000)

                # Reset take picture
                demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC,
                                                        0, 0,
                                                        ParameterMode.ABSOLUTE, 0)
                # Wait for 4000 ms
                demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                        ParameterMode.ABSOLUTE, 4000)

                demonstrator_program.execute()
    else:
        print('Connection cannot be established to the Demonstrator')
