#!/usr/bin/python

import pika
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program
from FAPSDemonstratorAPI.ApplicationConstants import *

print('pika version: %s' % pika.__version__)

if __name__ == '__main__':
    demonstrator_program = Program()
    if demonstrator_program.connect():
        demonstrator_program.reset()
        demonstrator_program.append_instruction(
            Command.CMD_SET_PATH_VELO,
            CommandMode.WCD,
            20,
            0,
            0,
            ParameterMode.ABSOLUTE,
            0
        )
        demonstrator_program.append_instruction(
            Command.CMD_POS_BASIC_SEGMENT,
            CommandMode.IM,
            PT_CURRENT,
            PT_MAGAZIN_1_CAMERA_POS,
            0,
            ParameterMode.ABSOLUTE,
            0
        )
        demonstrator_program.append_instruction(
            Command.CMD_WAIT_POS_BASIC_SEG_READY,
            CommandMode.WCD,
            0,
            0,
            0,
            ParameterMode.ABSOLUTE,
            20000
        )

        place_destination = MAGAZIN_POSITION_CAMERA[0]
        demonstrator_program.append_instruction(
            Command.CMD_POS_ABS_XYZ,
            CommandMode.WCD,
            place_destination[0],
            place_destination[1],
            place_destination[2],
            ParameterMode.ABSOLUTE,
            0
        )

        demonstrator_program.append_instruction(
            Command.CMD_SET_PATH_VELO,
            CommandMode.WCD,
            50,
            0,
            0,
            ParameterMode.ABSOLUTE,
            0
        )
        demonstrator_program.execute()
    else:
        print('Connection cannot be established to the Demonstrator')
