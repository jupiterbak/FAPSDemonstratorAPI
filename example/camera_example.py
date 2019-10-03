#!/usr/bin/python
import threading

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle

def periodic_main():
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
        # Wait for 500 ms
        demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                ParameterMode.ABSOLUTE, 500)
        # Reset take picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC,
                                                0, 0,
                                                ParameterMode.ABSOLUTE, 0)

        ## Second Picture
        demonstrator_program.append_instruction(
            Command.CMD_POS_REL_XYZ,
            CommandMode.WCD,
            -20,
            0,
            0,
            ParameterMode.ABSOLUTE,
            0
        )

        # Take a picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC, 1, 0,
                                                ParameterMode.ABSOLUTE, 0)
        # Wait for 500 ms
        demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                ParameterMode.ABSOLUTE, 500)
        # Reset take picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC,
                                                0, 0,
                                                ParameterMode.ABSOLUTE, 0)

        ## Third Picture
        demonstrator_program.append_instruction(
            Command.CMD_POS_REL_XYZ,
            CommandMode.WCD,
            0,
            20,
            0,
            ParameterMode.ABSOLUTE,
            0
        )

        # Take a picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC, 1, 0,
                                                ParameterMode.ABSOLUTE, 0)
        # Wait for 500 ms
        demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                ParameterMode.ABSOLUTE, 500)
        # Reset take picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC,
                                                0, 0,
                                                ParameterMode.ABSOLUTE, 0)

        ## Forth Picture
        demonstrator_program.append_instruction(
            Command.CMD_POS_REL_XYZ,
            CommandMode.WCD,
            20,
            0,
            0,
            ParameterMode.ABSOLUTE,
            0
        )

        # Take a picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC, 1, 0,
                                                ParameterMode.ABSOLUTE, 0)
        # Wait for 500 ms
        demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                ParameterMode.ABSOLUTE, 500)
        # Reset take picture
        demonstrator_program.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC,
                                                0, 0,
                                                ParameterMode.ABSOLUTE, 0)

        ## return to initial Position
        demonstrator_program.append_instruction(
            Command.CMD_POS_REL_XYZ,
            CommandMode.WCD,
            0,
            -20,
            0,
            ParameterMode.ABSOLUTE,
            0
        )
        # Wait for 500 ms
        demonstrator_program.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                                                ParameterMode.ABSOLUTE, 500)
        ## Execute
        demonstrator_program.execute()
        threading.Timer(10, periodic_main).start()
    else:
        print('Connection cannot be established to the Demonstrator')

if __name__ == '__main__':
    periodic_main()
