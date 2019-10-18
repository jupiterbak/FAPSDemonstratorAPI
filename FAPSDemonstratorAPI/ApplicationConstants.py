
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

PT_MAGAZIN_0_CAMERA_POS = 80
PT_MAGAZIN_1_CAMERA_POS = 81
PT_MAGAZIN_2_CAMERA_POS = 82
PT_MAGAZIN_3_CAMERA_POS = 83
PT_MAGAZIN_4_CAMERA_POS = 84

PT_MAGAZIN_ARRAY = [
    PT_MAGAZIN_0_CAMERA_POS,
    PT_MAGAZIN_1_CAMERA_POS,
    PT_MAGAZIN_2_CAMERA_POS,
    PT_MAGAZIN_3_CAMERA_POS,
    PT_MAGAZIN_4_CAMERA_POS
]

# Define program indexes
INDEX_START = 1
INDEX_MOVE_WAIT = 30
INDEX_MONTAGE = 100
INDEX_DEMONTAGE = 250
INDEX_ACTION_DONE = 400
INDEX_CLOUD_CMDS = 450
CLOUD_CMD_LENGTH = 500

# define Magazin
MAGAZINS_NAMES = ["MAGAZIN_0","MAGAZIN_1","MAGAZIN_2","MAGAZIN_3","MAGAZIN_4"]

MAGAZIN_POSITION_CAMERA = \
    [
        [610, 270, 150],
        [1000, 270, 150],
        [1440, 260, 150],
        [1850, 250, 150],
        [2360, 250, 150]
    ]

# Define product position camera
PRODUCT_POSITION_CAMERA = [1442, -94, 170]

PRODUCT_SINGLE_PLACE_POSITION = [1442, -94, 0]

PRODUCT_PLACE_POSITION_IN_BOX = [
    [1360, -78, 10.0],
    [1360, -230, 10.0],
    [1500, -78, 10.0],
    [1500, -230, 10.0]
]

