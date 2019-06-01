#!/usr/bin/python

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program
from random import shuffle

# Define Global Conditions
CND_INIT = 1
CND_FINISH = 2
CND_BASIC_SEG_PRE_STOP = 3
CND_NEW_PRODUCT = 4
CND_PRODUCT_DONE = 5
CND_GRIPPER_RDY_1 = 6
CND_GRIPPER_RDY_2 = 7
CND_GRIPPER_RDY_3 = 8
CND_PRODUCT_ACTION = 9
CND_PROGRAM_DONE = 17

CND_CAMERA_TAKE_PIC = 20
CND_GRIPPER_ON = 21
CND_GRIPPER_OPEN = 22
CND_CLOUD_CONNECTED = 23
CND_START_CLOUD_PGM = 24

# define basic segment points index
PT_CURRENT = 0
PT_WAIT = 1
PT_GRIPPER_1 = 2
PT_GRIPPER_1_VO_IN = 3
PT_GRIPPER_1_VO_OUT = 4
PT_GRIPPER_2 = 5
PT_GRIPPER_2_VO_IN = 6
PT_GRIPPER_2_VO_OUT = 7
PT_GRIPPER_3 = 8
PT_GRIPPER_3_VO_IN = 9
PT_GRIPPER_3_VO_OUT = 10
PT_GRIPPER_4 = 11
PT_GRIPPER_4_VO_IN = 12
PT_GRIPPER_4_VO_OUT = 13
PT_PRODUCT_1 = 14
PT_PRODUCT_2 = 15
PT_PRODUCT_3 = 16
PT_PRODUCT_4 = 17
PT_GRIPPER_REF = 18
PT_PRODUCT_REF = 19
PT_PRODUCT_CAMERA = 20

PT_PALLETE_0_START = 32
PT_PALLETE_0_CNT_X = 4
PT_PALLETE_0_CNT_Y = 4

PT_PALLETE_1_START = 48
PT_PALLETE_1_CNT_X = 4
PT_PALLETE_1_CNT_Y = 4

# Define program indexes
INDEX_START = 1
INDEX_MOVE_WAIT = 30
INDEX_MONTAGE = 100
INDEX_DEMONTAGE = 250
INDEX_ACTION_DONE = 400
INDEX_CLOUD_CMDS = 450
CLOUD_CMD_LENGTH = 500

STEPS = 3


class Demo:
    def __init__(self):
        self.demonstrator_program = Program()
        # define the product positions lists
        self.fromPositions = list(range(0, 16))
        self.toPositions = list(range(0, 16))
        self.start = datetime.now()
        self.current = datetime.now()
        self.task_montage = True

    def generateDemontageProgram(self, programObject):
        # Random Optimization
        # shuffle(self.fromPositions)
        # shuffle(self.toPositions)

        # ==============================================================================================================
        # Generate the program
        # ==============================================================================================================
        programObject.reset()
        # ==============================================================================================================
        programObject.append_instruction(Command.CMD_SET_PATH_VELO,
                                         CommandMode.WCD,
                                         100, 0, 0, ParameterMode.ABSOLUTE, 0)
        # ==============================================================================================================
        last_position = 0
        # Main For Loop
        for i in range(STEPS): # for i in range(16):
            # Wait for 200 ms
            programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                             200)
            # Open the gripper
            programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 1, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Move to Origin
            if (i == 0):
                programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, PT_CURRENT,
                                                 PT_PALLETE_1_START + self.toPositions[i], 0, ParameterMode.ABSOLUTE,
                                                 0)
                last_position = PT_PALLETE_1_START + self.toPositions[i]
            else:
                programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, last_position,
                                                 PT_PALLETE_1_START + self.toPositions[i], 0, ParameterMode.ABSOLUTE,
                                                 0)
                last_position = PT_PALLETE_1_START + self.toPositions[i]
            # Wait until movement is finished
            programObject.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Close the gripper
            programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 0, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Wait for 200 ms
            programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                             200)
            # Move to Target Pos
            programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, last_position,
                                             PT_PALLETE_0_START + self.fromPositions[i], 0, ParameterMode.ABSOLUTE, 0)
            last_position = PT_PALLETE_0_START + self.fromPositions[i]
            # Wait until movement is finished
            programObject.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Wait for 200 ms
            programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                             200)
            # Open the gripper
            programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 1, 0,
                                             ParameterMode.ABSOLUTE, 0)

        # End Main  for Loop
        # ==============================================================================================================
        # Wait for 200 ms
        programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                         200)
        # Goto to camera position
        programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, last_position,
                                         PT_PRODUCT_CAMERA, 0, ParameterMode.ABSOLUTE, 0)
        # Wait until movement is finished
        programObject.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # Open the gripper
        programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 1, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # set Condition product wurde montiert
        programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_PRODUCT_ACTION, 1, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # Signal production is done
        programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_PRODUCT_DONE, 1, 0,
                                         ParameterMode.ABSOLUTE, 0)

        # Wait for 4000 ms
        programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE, 4000)
        # Check End of the program?
        programObject.append_instruction(Command.CMD_JMPN, CommandMode.WCD, INDEX_MOVE_WAIT, CND_FINISH, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # ==============================================================================================================
        return programObject

    def generateMontageProgram(self, programObject):
        # Random Optimization
        # shuffle(self.fromPositions)
        # shuffle(self.toPositions)

        # ==============================================================================================================
        # Generate the program
        # ==============================================================================================================
        programObject.reset()
        # ==============================================================================================================
        programObject.append_instruction(Command.CMD_SET_PATH_VELO,
                                         CommandMode.WCD,
                                         100, 0, 0, ParameterMode.ABSOLUTE, 0)
        # ==============================================================================================================
        last_position = 0
        # Main For Loop
        for i in range(STEPS): # for i in range(16):
            # Wait for 200 ms
            programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                             200)
            # Open the gripper
            programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 1, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Move to Origin
            if (i == 0):
                programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, PT_CURRENT,
                                                 PT_PALLETE_0_START + self.fromPositions[i], 0, ParameterMode.ABSOLUTE,
                                                 0)
                last_position = PT_PALLETE_0_START + self.fromPositions[i]
            else:
                programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, last_position,
                                                 PT_PALLETE_0_START + self.fromPositions[i], 0, ParameterMode.ABSOLUTE,
                                                 0)
                last_position = PT_PALLETE_0_START + self.fromPositions[i]
            # Wait until movement is finished
            programObject.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Close the gripper
            programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 0, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Wait for 200 ms
            programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                             200)
            # Move to Target Pos
            programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, last_position,
                                             PT_PALLETE_1_START + self.toPositions[i], 0, ParameterMode.ABSOLUTE, 0)
            last_position = PT_PALLETE_1_START + self.toPositions[i]
            # Wait until movement is finished
            programObject.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                             ParameterMode.ABSOLUTE, 0)
            # Wait for 200 ms
            programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                             200)
            # Open the gripper
            programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 1, 0,
                                             ParameterMode.ABSOLUTE, 0)

        # End Main  for Loop
        # ==============================================================================================================
        # Wait for 200 ms
        programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE,
                                         200)
        # Goto to camera position
        programObject.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, last_position,
                                         PT_PRODUCT_CAMERA, 0, ParameterMode.ABSOLUTE, 0)
        # Wait until movement is finished
        programObject.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # Open the gripper
        programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_GRIPPER_OPEN, 1, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # set Condition product wurde montiert
        programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_PRODUCT_ACTION, 1, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # Signal production is done
        programObject.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_PRODUCT_DONE, 1, 0,
                                         ParameterMode.ABSOLUTE, 0)

        # Wait for 4000 ms
        programObject.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0, ParameterMode.ABSOLUTE, 4000)
        # Check End of the program?
        programObject.append_instruction(Command.CMD_JMPN, CommandMode.WCD, INDEX_MOVE_WAIT, CND_FINISH, 0,
                                         ParameterMode.ABSOLUTE, 0)
        # ==============================================================================================================
        return programObject

    def mycallback(self, ch, method, properties, json_data):
        body = json.loads(json_data)
        value = body["value"]
        data = value["data"]
        demonstrator_program_counter = data['i32ActualProgrammPointer#']
        demonstrator_is_running = data['i32ProgrammRunning#']
        demonstrator_product_ready = data['product_ready#']

        # Generate dummy FAPSDemonstratorAPI
        if (not (demonstrator_is_running is None)) \
                and (demonstrator_program_counter == 448) \
                and (demonstrator_product_ready != 0):
            self.current = datetime.now()
            delta = self.current - self.start
            if (delta.total_seconds() > 20):
                if self.task_montage:
                    myprogram = self.generateMontageProgram(self.demonstrator_program)
                else:
                    myprogram = self.generateDemontageProgram(self.demonstrator_program)
                print(delta.total_seconds())
                myprogram.execute()
                self.task_montage = not self.task_montage
                self.start = datetime.now()


if __name__ == '__main__':
    print('Demonstrator Programm Api using pika version: %s' % pika.__version__)
    demo = Demo()
    if demo.demonstrator_program.connect():
        # Initialize the listener to the Demonstrator FAPSDemonstratorAPI pointer using the FAPSDemonstratorAPI
        connection = demo.demonstrator_program.connection
        channel = connection.channel()

        channel.exchange_declare(
            exchange='AMQPStreamer_1',
            passive=True,
            durable=False,
            exchange_type='fanout'
        )

        queue = channel.queue_declare(
            queue='DEMONSTRATOR_PROGRAM_API_DATA',
            durable=False,
            exclusive=False,
            auto_delete=True
        ).method.queue
        channel.queue_bind(exchange='AMQPStreamer_1', queue=queue, routing_key='')

        # bind the call back to the demonstrator FAPSDemonstratorAPI and start listening
        channel.basic_consume(demo.mycallback, queue=queue, no_ack=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            connection.close()
            exit(0)
    else:
        print('Connection cannot be made to the demonstrator')
