#!/usr/bin/python

import pika
import FAPSDemonstratorAPI

print('pika version: %s' % pika.__version__)

if __name__ == '__main__':
    demonstrator_program = FAPSDemonstratorAPI.Program()
    if demonstrator_program.connect():

                demonstrator_program.reset()
                demonstrator_program.append_instruction(FAPSDemonstratorAPI.Command.CMD_SET_VELO,
                                                        FAPSDemonstratorAPI.CommandMode.WCD,
                                                        20, 0, 0, FAPSDemonstratorAPI.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.append_instruction(FAPSDemonstratorAPI.Command.CMD_POS_REL_XYZ,
                                                        FAPSDemonstratorAPI.CommandMode.WCD,
                                                        100, 0, 0, FAPSDemonstratorAPI.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.append_instruction(FAPSDemonstratorAPI.Command.CMD_POS_REL_XYZ,
                                                        FAPSDemonstratorAPI.CommandMode.WCD,
                                                        -100, 0, 0, FAPSDemonstratorAPI.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.append_instruction(FAPSDemonstratorAPI.Command.CMD_SET_VELO,
                                                        FAPSDemonstratorAPI.CommandMode.WCD,
                                                        50, 0, 0, FAPSDemonstratorAPI.ParameterMode.ABSOLUTE, 0)
                demonstrator_program.execute()
    else:
        print('Connection cannot be made to the demonstrator')
