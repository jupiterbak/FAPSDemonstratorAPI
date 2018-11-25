from enum import Enum, unique


class ParameterMode(Enum):
    """This class is hold the different instruction command mode."""

    ABSOLUTE = 0
    RV_DATA = 1
    default = ABSOLUTE
