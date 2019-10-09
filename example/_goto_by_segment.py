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
            Command.CMD_POS_BASIC_SEGMENT,
            CommandMode.WCD,
            PT_CURRENT,
            PT_MAGAZIN_1_CAMERA_POS,
            0,
            ParameterMode.ABSOLUTE,
            0
        )
        demonstrator_program.append_instruction(
            Command.CMD_POS_BASIC_SEGMENT,
            CommandMode.WCD,
            PT_MAGAZIN_1_CAMERA_POS,
            PT_MAGAZIN_2_CAMERA_POS,
            0,
            ParameterMode.ABSOLUTE,
            0
        )

        demonstrator_program.execute()
    else:
        print('Connection cannot be established to the Demonstrator')
