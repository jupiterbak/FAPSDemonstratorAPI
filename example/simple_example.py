#!/usr/bin/python

import pika
import time
import json
from program import program,command,parameter_mode,command_mode

print('pika version: %s' % pika.__version__)

if __name__ == '__main__':
    demonstrator_program = program.Program()
    if demonstrator_program.connect():

                demonstrator_program.reset()
                demonstrator_program.append_instruction(command.Command.CMD_SET_VELO,command_mode.CommandMode.WCD,
                                                        20,0,0,parameter_mode.ParameterMode.ABSOLUTE,0)
                demonstrator_program.append_instruction(command.Command.CMD_POS_REL_XYZ, command_mode.CommandMode.WCD,
                                                        100, 0, 0, parameter_mode.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.append_instruction(command.Command.CMD_POS_REL_XYZ, command_mode.CommandMode.WCD,
                                                        -100, 0, 0, parameter_mode.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.append_instruction(command.Command.CMD_SET_VELO, command_mode.CommandMode.WCD,
                                                        50, 0, 0, parameter_mode.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.execute()
    else:
        print('Connection cannot be made to the demonstrator')
