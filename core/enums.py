from enum import Enum


class PlayerState(str, Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
