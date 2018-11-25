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
        self.PROGRAM_MAX_LENGTH = 500
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
                passive=True,
                durable=False,
                exchange_type='fanout'
            )
            self.channel.queue_declare(
                queue='DEMONSTRATOR_PROGRAM_API_{}'.format(int(round(time.time() * 1000))),
                durable=False,
                passive=True,
                exclusive=False,
                auto_delete=True
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
        try:
            if self.connected:
                # Turn on delivery confirmations
                self.channel.confirm_delivery()
                return self.channel.basic_publish('AMQPStreamer_Exchange_ProgramFromCloud', '', self.get_all_json(),
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
        return json.dumps(self.instructions, ensure_ascii=False)

    def get_all_json(self):
        """
        Return the instructions of the FAPSDemonstratorAPI as a list. Fill unspecified instructions.
        """
        if len(self.instructions) < self.PROGRAM_MAX_LENGTH:
            return json.dumps(self.get_all_instructions(), ensure_ascii=False)
        else:
            return self.get_json()

    def __str__(self):
        return ''.join(self.instructions)

    def __len__(self):
        return len(self.instructions)
