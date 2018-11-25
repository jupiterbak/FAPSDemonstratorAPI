# FAPSDemonstratorAPI
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

    pip install FAPSDemonstratorAPI

Install from github for the latest changes:

::

    pip install https://github.com/jupiterbak/DEMONSTRATOR_PROGRAM_API.git

If you have the files checked out for development:

::

    git clone https://github.com/jupiterbak/DEMONSTRATOR_PROGRAM_API.git
    cd DEMONSTRATOR_PROGRAM_API
    python setup.py -f

Example
-------
Here is the most simple example of use, generate a new program and execute it.
Please make sure you are in the FAPS Network:

.. code :: python

    import FAPSDemonstratorAPI    
    demonstrator_program = FAPSDemonstratorAPI.Program()
    if demonstrator_program.connect():
                demonstrator_program.reset()
                demonstrator_program.append_instruction(
                    FAPSDemonstratorAPI.Command.CMD_SET_VELO,
                    FAPSDemonstratorAPI.CommandMode.WCD,
                    20,
                    0,
                    0,
                    FAPSDemonstratorAPI.ParameterMode.ABSOLUTE,
                    0
                )
                demonstrator_program.append_instruction(
                    FAPSDemonstratorAPI.Command.CMD_POS_REL_XYZ,
                    FAPSDemonstratorAPI.CommandMode.WCD,
                    100,
                    0,
                    0,
                    FAPSDemonstratorAPI.ParameterMode.ABSOLUTE,
                    0
                )
                demonstrator_program.append_instruction(
                    FAPSDemonstratorAPI.Command.CMD_POS_REL_XYZ,
                    FAPSDemonstratorAPI.CommandMode.WCD,
                    -100,
                    0,
                    0,
                    FAPSDemonstratorAPI.ParameterMode.ABSOLUTE,
                    0
                )
                demonstrator_program.append_instruction(
                    FAPSDemonstratorAPI.Command.CMD_SET_VELO,
                    FAPSDemonstratorAPI.CommandMode.WCD,
                    50,
                    0,
                    0,
                    FAPSDemonstratorAPI.ParameterMode.ABSOLUTE,
                    0
                )
                demonstrator_program.execute()
    else:
        print('Connection cannot be established to the Demonstrator')
  
Credits
=======
Jupiter Bakakeu (jupiter.bakakeu@faps.fau.de/jupiter.bakakeu@gmail.com)
   
License
=======
Licensed under the MIT License. See COPYING for details.
