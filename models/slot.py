from dataclasses import dataclass


@dataclass
class Slot:
    label: str = ""
    file: str = ""
    hotkey: str = ""
    color: str = "#2a2a2a"
