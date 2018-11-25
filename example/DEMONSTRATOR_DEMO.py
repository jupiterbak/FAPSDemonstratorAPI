#!/usr/bin/python

import pika
import time
import json
import FAPSDemonstratorAPI

if __name__ == '__main__':
    print('Demonstrator Programm Api using pika version: %s' % pika.__version__)

    # Initialize the FAPSDemonstratorAPI
    demonstrator_program = FAPSDemonstratorAPI.Program()
    if demonstrator_program.connect():
        # Initialize the listener to the Demonstrator FAPSDemonstratorAPI pointer using the FAPSDemonstratorAPI
        connection = demonstrator_program.connection
        channel = connection.channel()

        channel.exchange_declare(
            exchange='AMQPStreamer_1',
            passive=True,
            durable=False,
            exchange_type='fanout'
        )

        queue = channel.queue_declare(
            queue='DEMONSTRATOR_PROGRAM_API_DATA_{}'.format(int(round(time.time() * 1000))),
            durable=False,
            exclusive=False,
            auto_delete=True
        ).method.queue
        channel.queue_bind(exchange='AMQPStreamer_1', queue=queue, routing_key='')

        # bind the call back to the demonstrator FAPSDemonstratorAPI and start listening
        def mycallback(ch, method, properties, body):
            body = json.loads(body)
            print('receive new data..')
            demonstrator_program_counter = body.value.data['i32ActualProgrammPointer#']
            demonstrator_is_running = body.value.data['i32ProgrammRunning#']

            # Generate dummy FAPSDemonstratorAPI
            if (not (demonstrator_is_running is None)) \
                    and (demonstrator_program_counter == demonstrator_program.PROGRAM_MAX_LENGTH-2):
                demonstrator_program.reset()
                demonstrator_program.append_instruction(FAPSDemonstratorAPI.Command.CMD_SET_VELO,
                                                        FAPSDemonstratorAPI.CommandMode.WCD,
                                                        20,0,0,FAPSDemonstratorAPI.ParameterMode.ABSOLUTE,0)
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

        channel.basic_consume( mycallback, queue=queue, no_ack=True)
        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            connection.close()
            exit(0)
    else:
        print('Connection cannot be made to the demonstrator')
