import random

from FAPSDemonstratorAPI import Program, Command, CommandMode, ParameterMode
from FAPSDemonstratorAPI.ApplicationConstants import *


def set_velocity(target_velocity=None, execute=False):
    # Check the parameter
    if target_velocity is None :
        return []
    temp = Program()
    if execute is True:
        temp.reset()

    # set the velocity to 20%
    temp.append_instruction(
        Command.CMD_SET_PATH_VELO,
        CommandMode.WCD,
        target_velocity,
        0,
        0,
        ParameterMode.ABSOLUTE,
        0
    )
    cmd_list = temp.get_instructions()

    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def goto_position(x=None, y=None, z=None, positioning_mode=None, execute=False):
    # Check the parameter
    if (x is None) or (y is None) or (z is None):
        return []
    temp = Program()
    if execute is True:
        temp.reset()

    # Go to the target position
    temp.append_instruction(
        Command.CMD_POS_ABS_XYZ if positioning_mode == "Absolute" else Command.CMD_POS_REL_XYZ,
        CommandMode.WCD,
        x,
        y,
        z,
        ParameterMode.ABSOLUTE,
        0
    )

    # Wait until movement is finished
    # temp.append_instruction(
    #     Command.CMD_WAIT_FOR_PATH_POSITION,
    #     CommandMode.WCD,
    #     5.0, -1, 0,
    #     ParameterMode.ABSOLUTE,
    #     0)

    cmd_list = temp.get_instructions()
    if execute is True:
        temp.execute()

    return cmd_list


def goto_product_camera_position(execute=False):
    # Check the parameter
    # nothing to do
    temp = Program()
    if execute is True:
        temp.reset()

    # set the velocity to 20%
    temp.append_instruction(
        Command.CMD_SET_PATH_VELO,
        CommandMode.WCD,
        30,
        0,
        0,
        ParameterMode.ABSOLUTE,
        0
    )
    # Goto to camera position
    temp.append_instruction(Command.CMD_POS_BASIC_SEGMENT, CommandMode.WCD, 0,
                            PT_PRODUCT_CAMERA, 0, ParameterMode.ABSOLUTE, 0)
    # Wait until movement is finished
    temp.append_instruction(Command.CMD_WAIT_POS_BASIC_SEG_END, CommandMode.WCD, 0, 0, 0,
                            ParameterMode.ABSOLUTE, 0)

    cmd_list = temp.get_instructions()
    if execute is True:
        temp.execute()

    return cmd_list


def take_picture(execute=False):
    # Check the parameter
    # nothing to do
    temp = Program()
    if execute is True:
        temp.reset()

    # Take a picture
    temp.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC, 1, 0,
                            ParameterMode.ABSOLUTE, 0)
    # Wait for 500 ms
    temp.append_instruction(Command.CMD_WAIT_TIME, CommandMode.WCD, 0, 0, 0,
                            ParameterMode.ABSOLUTE, 500)

    # Reset take picture
    temp.append_instruction(Command.CMD_SET_CONDITION, CommandMode.WCD, CND_CAMERA_TAKE_PIC,
                            0, 0,
                            ParameterMode.ABSOLUTE, 0)

    cmd_list = temp.get_instructions()
    if execute is True:
        temp.execute()

    return cmd_list


def goto_product_camera_position_and_take_picture(execute=False):
    # Check the parameter
    # nothing to do
    temp = Program()
    if execute is True:
        temp.reset()

    # Go to prosuct camera position
    temp.append_all_instructions(goto_product_camera_position())

    # Go to prosuct camera position
    temp.append_all_instructions(goto_product_camera_position())

    cmd_list = temp.get_instructions()
    if execute is True:
        temp.execute()

    return cmd_list


def take_product_picture(execute=False):
    return goto_product_camera_position_and_take_picture(execute)


def goto_magazin_camera_position(magazin_index=None, execute=False):
    # Check the parameter
    if magazin_index is None:
        return []
        # get the position
    m_position = MAGAZIN_POSITION_CAMERA[magazin_index]
    if m_position is None or len(m_position) < 3:
        return []

    temp = Program()
    if execute is True:
        temp.reset()
    # set the velocity to 20%
    temp.append_instruction(
        Command.CMD_SET_PATH_VELO,
        CommandMode.WCD,
        30,
        0,
        0,
        ParameterMode.ABSOLUTE,
        0
    )
    # Goto the position
    temp.append_instruction(
        Command.CMD_POS_ABS_XYZ,
        CommandMode.WCD,
        m_position[0],
        m_position[1],
        m_position[2],
        ParameterMode.ABSOLUTE,
        0
    )

    # Wait until movement is finished
    # temp.append_instruction(
    #     Command.CMD_WAIT_FOR_PATH_POSITION,
    #     CommandMode.WCD,
    #     5.0, -1, 0,
    #     ParameterMode.ABSOLUTE,
    #     0
    # )

    cmd_list = temp.get_instructions()
    if execute is True:
        temp.execute()

    return cmd_list


def goto_magazin_and_take_picture(magazin_index=None, execute=False):
    # Check the parameter
    if magazin_index is None:
        return []
        # get the position
    m_position = MAGAZIN_POSITION_CAMERA[magazin_index]
    if m_position is None or len(m_position) < 3:
        return []

    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    # Append all instructions
    temp.append_all_instructions(goto_magazin_camera_position(magazin_index, execute=False))
    temp.append_all_instructions(take_picture(execute=False))

    cmd_list = temp.get_instructions()

    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def scan_magazin(magazin_index=None, execute=False):
    # Check the parameter
    if magazin_index is None:
        return []
        # get the position
    m_position = MAGAZIN_POSITION_CAMERA[magazin_index]
    if m_position is None or len(m_position) < 3:
        return []

    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    # Append all instructions
    # Go to the target position
    temp.append_all_instructions(goto_magazin_camera_position(magazin_index, execute=False))

    # Start scanning
    # Move -50 mm  in the x direction
    temp.append_all_instructions(goto_position(-50.0, 0.0, 0.0, positioning_mode="Relative", execute=False))
    # Take a first picture
    temp.append_all_instructions(take_picture(execute=False))

    # Move 100 mm  in the x direction
    temp.append_all_instructions(goto_position(100.0, 0.0, 0.0, positioning_mode="Relative", execute=False))
    # Take a second picture
    temp.append_all_instructions(take_picture(execute=False))

    # Move -50 mm  in the x direction and 10 mm in the y direction
    temp.append_all_instructions(goto_position(-50.0, 0.0, 0.0, positioning_mode="Relative", execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def scan_all_magazins(execute=False):
    # Check the parameter
    # Nothing to do
    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    for i in range(len(MAGAZIN_POSITION_CAMERA)):
        temp.append_all_instructions(scan_magazin(i, execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def scan_product(execute=False):
    # Check the parameter
    # Nothing to do

    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    # Append all instructions
    # Go to the target position
    temp.append_all_instructions(goto_product_camera_position(execute=False))

    # Start scanning
    temp.append_all_instructions(goto_position(40.0, 50.0, 0.0, positioning_mode="Relative", execute=False))
    # Take a first picture
    temp.append_all_instructions(take_picture(execute=False))

    # Move -20 mm  in the x direction
    temp.append_all_instructions(goto_position(-80.0, 0.0, 0.0, positioning_mode="Relative", execute=False))
    # Take a second picture
    temp.append_all_instructions(take_picture(execute=False))

    # Move -20 mm forward in the y direction
    temp.append_all_instructions(goto_position(0.0, -50.0, 0.0, positioning_mode="Relative", execute=False))
    # Take a third picture
    temp.append_all_instructions(take_picture(execute=False))

    # Move 20 mm forward in the x direction
    temp.append_all_instructions(goto_position(80.0, 0.0, 0.0, positioning_mode="Relative", execute=False))
    # Take a fourth picture
    temp.append_all_instructions(take_picture(execute=False))

    # Move -10 mm  in the x direction and 10 mm in the y direction
    temp.append_all_instructions(goto_position(-40.0, 0.0, 0.0, positioning_mode="Relative", execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()
    return cmd_list


def calibrate_magazin(magazin_index=None, execute=False):
    # Check the parameter
    if magazin_index is None:
        return []
        # get the position
    m_position = MAGAZIN_POSITION_CAMERA[magazin_index]
    if m_position is None or len(m_position) < 3:
        return []

    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    # Append all instructions
    # Go to the target position
    temp.append_all_instructions(goto_magazin_camera_position(magazin_index, execute=False))

    # Take a picture
    temp.append_all_instructions(take_picture(execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def calibrate_all_magazins(execute=False):
    # Check the parameter
    # Nothing to do
    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    for i in range(len(MAGAZIN_POSITION_CAMERA)):
        temp.append_all_instructions(calibrate_magazin(i, execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list

def calibrate_camera( execute=False):
    # Check the parameter
    # We will consider only the 4th magazin position
    m_position = MAGAZIN_POSITION_CAMERA[4]
    if m_position is None or len(m_position) < 3:
        return []

    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    # Append all instructions
    # set the velocity to 20%
    temp.append_instruction(
        Command.CMD_SET_PATH_VELO,
        CommandMode.WCD,
        30,
        0,
        0,
        ParameterMode.ABSOLUTE,
        0
    )
    # Goto the random position and take 10 pictures
    for i in range(10):
        # Go to the position
        temp.append_instruction(
            Command.CMD_POS_ABS_XYZ,
            CommandMode.WCD,
            m_position[0] + random.randint(-30, 30),
            m_position[1] + random.randint(-30, 30),
            m_position[2],
            ParameterMode.ABSOLUTE,
            0
        )
        # Take a picture
        temp.append_all_instructions(take_picture(execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def calibrate_product(execute=False):
    # Check the parameter
    m_position = PRODUCT_POSITION_CAMERA
    if m_position is None or len(m_position) < 3:
        return []

    # Initialize the programm
    temp = Program()
    if execute is True:
        temp.reset()

    # Append all instructions
    # Go to the target position
    temp.append_instruction(
        Command.CMD_POS_ABS_XYZ,
        CommandMode.WCD,
        m_position[0],
        m_position[1],
        m_position[2],
        ParameterMode.ABSOLUTE,
        0
    )

    # Take a picture
    temp.append_all_instructions(take_picture(execute=False))

    cmd_list = temp.get_instructions()
    # Execute the program
    if execute is True:
        temp.execute()

    return cmd_list


def take_gripper(gripper_index=None, execute=False):
    # Not implemented
    return []


def pick_object(object_position=None, execute=False):
    # Not implemented
    return []


def take_object(object_position=None, execute=False):
    return pick_object(object_position,execute)


def place_object(place_object_position=None, execute=False):
    # Not implemented
    return []


def pick_and_place_object(object_position=None, place_object_position=None, execute=False):
    # Not implemented
    return []