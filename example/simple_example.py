#!/usr/bin/python

import pika
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program

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
                    Command.CMD_POS_REL_XYZ,
                    CommandMode.WCD,
                    10,
                    0,
                    0,
                    ParameterMode.ABSOLUTE,
                    0
                )
                demonstrator_program.append_instruction(
                    Command.CMD_POS_REL_XYZ,
                    CommandMode.WCD,
                    -10,
                    0,
                    0,
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
