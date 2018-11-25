from enum import Enum, unique


class CommandMode(Enum):
    """This class is hold the different instruction command mode."""

    WCD = 0
    IM = 1

    default = WCD
