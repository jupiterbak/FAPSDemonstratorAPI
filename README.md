# DEMONSTRATOR_PROGRAM_API
====
'DEMONSTRATOR_PROGRAM_API' is a RabbitMQ (AMQP-0-9-1) client library to control the faps I4.0 demonstrator by generating
 a set of instructions.

|Version| |Python versions| |Status| |Coverage| |License| |Docs|

Introduction
-------------
- Python 2.7 and 3.4+ are supported.

- The implementation is based on the library Pika.

- Since threads aren't appropriate to every situation, it doesn't
  require threads.

Install
=======

Install from pip for the latest stable release (not avialble now):

::

    pip install DEMONSTRATOR_PROGRAM_API

Install from github for the latest changes:

::

    pip install https://github.com/jupiterbak/DEMONSTRATOR_PROGRAM_API.git

If you have the files checked out for development:

::

    git clone https://github.com/jupiterbak/DEMONSTRATOR_PROGRAM_API.git
    cd DEMONSTRATOR_PROGRAM_API
    python setup.py

Example
-------
Here is the most simple example of use, generate a new program and execute it.
Please make sure you are in the FAPS Network:

.. code :: python

    import DEMONSTRATOR_PROGRAM_API
    from DEMONSTRATOR_PROGRAM_API.program import program,command,parameter_mode,command_mode
    
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

And an example of writing a blocking consumer:

.. code :: python

    import pika
    connection = pika.BlockingConnection()
    channel = connection.channel()

    for method_frame, properties, body in channel.consume('test'):

        # Display the message parts and ack the message
        print(method_frame, properties, body)
        channel.basic_ack(method_frame.delivery_tag)

        # Escape out of the loop after 10 messages
        if method_frame.delivery_tag == 10:
            break

    # Cancel the consumer and return any pending messages
    requeued_messages = channel.cancel()
    print('Requeued %i messages' % requeued_messages)
    connection.close()
    
License
=======
Licensed under the BSD License. See COPYING for details.
See jsonpickleJS/LICENSE for details about the jsonpickleJS license.
