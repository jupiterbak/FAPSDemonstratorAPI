#!/usr/bin/env python
import pika
from FAPSDemonstratorAPI import command, command_mode, parameter_mode
import json
import time



class Program:
    """This class is the class holdinfg the set of instruction that will be executed to the demonstrator."""

    def __init__(self):
        """
            Responsible for generating the set of instructions.
        """

        # Define global constants
        # Define Global Conditions
        self.CND_INIT = 1
        self.CND_FINISH = 2
        self.CND_BASIC_SEG_PRE_STOP = 3
        self.CND_NEW_PRODUCT = 4
        self.CND_PRODUCT_DONE = 5
        self.CND_GRIPPER_RDY_1 = 6
        self.CND_GRIPPER_RDY_2 = 7
        self.CND_GRIPPER_RDY_3 = 8
        self.CND_PRODUCT_ACTION = 9
        self.CND_PROGRAM_DONE = 17

        self.CND_CAMERA_TAKE_PIC = 20
        self.CND_GRIPPER_ON = 21
        self.CND_GRIPPER_OPEN = 22
        self.CND_CLOUD_CONNECTED = 23
        self.CND_START_CLOUD_PGM = 24

        # define basic segment points index
        self.PT_CURRENT = 0
        self.PT_WAIT = 1
        self.PT_GRIPPER_1 = 2
        self.PT_GRIPPER_1_VO_IN = 3
        self.PT_GRIPPER_1_VO_OUT = 4
        self.PT_GRIPPER_2 = 5
        self.PT_GRIPPER_2_VO_IN = 6
        self.PT_GRIPPER_2_VO_OUT = 7
        self.PT_GRIPPER_3 = 8
        self.PT_GRIPPER_3_VO_IN = 9
        self.PT_GRIPPER_3_VO_OUT = 10
        self.PT_GRIPPER_4 = 11
        self.PT_GRIPPER_4_VO_IN = 12
        self.PT_GRIPPER_4_VO_OUT = 13
        self.PT_PRODUCT_1 = 14
        self.PT_PRODUCT_2 = 15
        self.PT_PRODUCT_3 = 16
        self.PT_PRODUCT_4 = 17
        self.PT_GRIPPER_REF = 18
        self.PT_PRODUCT_REF = 19
        self.PT_PRODUCT_CAMERA = 20

        self.PT_PALLETE_0_START = 32
        self.PT_PALLETE_0_CNT_X = 4
        self.PT_PALLETE_0_CNT_Y = 4

        self.PT_PALLETE_1_START = 48
        self.PT_PALLETE_1_CNT_X = 4
        self.PT_PALLETE_1_CNT_Y = 4

        # Define program indexes
        self.INDEX_START = 1
        self.INDEX_MOVE_WAIT = 30
        self.INDEX_MONTAGE = 100
        self.INDEX_DEMONTAGE = 250
        self.INDEX_ACTION_DONE = 400
        self.INDEX_CLOUD_CMDS = 450
        self.CLOUD_CMD_LENGTH = 500

        self.PROGRAM_MAX_LENGTH = 500
        self.INDEX_CLOUD_CMDS = 450
        self.RETURN_INDEX = self.INDEX_CLOUD_CMDS -2
        self.DEMONSTRATOR_ENDPOINT = "cloud.faps.uni-erlangen.de"
        self.instructions = []
        self.connection = None
        self.channel = None
        self.connected = False

    def connect(self):
        """
            Connect the FAPSDemonstratorAPI to the demonstrator.
        :return true if the connect has been established or false otherwise.
        """
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                port=5672,
                host=self.DEMONSTRATOR_ENDPOINT,
                credentials=pika.PlainCredentials('esys', 'esys'))
            )
            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange='AMQPStreamer_Exchange_ProgramFromCloud',
                durable=False,
                exchange_type='fanout'
            )

            self.connected = True
            return True
        except Exception:
            if not (self.channel is None):
                self.channel.close()
                self.channel = None
            if not (self.connection is None):
                self.connection.close()
                self.connection = None
            self.connected = False
            return False

    def execute(self):
        """
           Execute the current FAPSDemonstratorAPI. Make sure the Demonstrator is configured.
        """
        if len(self.instructions) > self.PROGRAM_MAX_LENGTH - 1:
            print("Warning: Program length %s is bigger than the maximum program lenth %s",self.instructions, self.PROGRAM_MAX_LENGTH - 1)
            return False
        try:
            if self.connected:
                # Add a return instruction to ensure a safe return
                self.append_instruction(
                    command.Command.CMD_JUMP_TO_SETNUMBER,
                    command_mode.CommandMode.WCD,
                    self.RETURN_INDEX,  # position
                    0,  # -
                    0,  # -
                    parameter_mode.ParameterMode.ABSOLUTE,
                    0
                )
                # Turn on delivery confirmations
                self.channel.confirm_delivery()
                return self.channel.basic_publish('FAPS_DEMONSTRATOR_ProgramManagement_ProgramFromCloud', '', self.get_json(),
                                                  pika.BasicProperties(delivery_mode=1))
            else:
                return False
        except Exception:
            return False

    def reset(self):
        """
            Reset the FAPSDemonstratorAPI instruction.
        """
        self.instructions = []

    def append_instruction(self, cmd=command.Command.CMD_NONE, cmd_mode=command_mode.CommandMode.IM, parameter1=0,
                           parameter2=0, parameter3=0, param_mode=parameter_mode.ParameterMode.ABSOLUTE, delay=0):
        """
        Add an instruction to the FAPSDemonstratorAPI.
        :param cmd: Instruction command.
        :param cmd_mode: Mode of the instruction command.
        :param parameter1: Command parameter 1.
        :param parameter2: Command parameter 2.
        :param parameter3: Command parameter 3.
        :param param_mode: Command parameter mode.
        :param delay: command delay in ms.
        """
        self.instructions.append(
            {
                "eCmd": cmd.name,
                "eMode": cmd_mode.name,
                "aParameter1": parameter1,
                "aParameter2": parameter2,
                "aParameter3": parameter3,
                "eParameterMode": param_mode.name,
                "tMon": delay
            }
        )

    def append_all_instructions(self, instruction_list):
        """
        Insert a list of instructions to the FAPSDemonstratorAPI.
        Note: We are not testing if the instructions are valid.
        :param index: Instruction command.
        """
        for instruction in instruction_list:
            self.instructions.append(instruction)


    def insert_command(self, index=0, cmd=command.Command.CMD_NONE, cmd_mode=command_mode.CommandMode.IM, parameter1=0,
                       parameter2=0, parameter3=0, param_mode=parameter_mode.ParameterMode.ABSOLUTE, delay=0):
        """
        Insert an instruction to the FAPSDemonstratorAPI.
        :param index: Instruction command.
        :param cmd: Instruction command.
        :param cmd_mode: Mode of the instruction command.
        :param parameter1: Command parameter 1.
        :param parameter2: Command parameter 2.
        :param parameter3: Command parameter 3.
        :param param_mode: Command parameter mode.
        :param delay: command delay in ms.
        """
        self.instructions.insert(
            index,
            {
                "eCmd": cmd.name,
                "eMode": cmd_mode.name,
                "aParameter1": parameter1,
                "aParameter2": parameter2,
                "aParameter3": parameter3,
                "eParameterMode": param_mode.name,
                "tMon": delay
            }
        )

    def pop(self, index=0):
        """
        Pop the last instruction at a specified index.
        :param index: Instruction command.
        """
        self.instructions.pop(index)

    def get_instructions(self):
        """
        Return the instructions of the FAPSDemonstratorAPI as a list.
        """
        return self.instructions

    def get_all_instructions(self):
        """
        Return the instructions of the FAPSDemonstratorAPI as a list. Fill unspecified instructions.
        """
        while len(self.instructions) < self.PROGRAM_MAX_LENGTH:
            self.append_instruction()
        return self.instructions

    def get_json(self):
        """
        Return the instruction of the FAPSDemonstratorAPI as JSON-Array.
        """
        return json.dumps(self.get_instructions(), ensure_ascii=False)

    def get_all_json(self):
        """
        Return the instructions of the FAPSDemonstratorAPI as a list. Fill unspecified instructions.
        """
        if len(self.instructions) < self.PROGRAM_MAX_LENGTH:
            obj = json.dumps(self.get_all_instructions(), ensure_ascii=False)
            return obj
        else:
            return self.get_json()

    def __str__(self):
        return ''.join(self.instructions)

    def __len__(self):
        return len(self.instructions)
