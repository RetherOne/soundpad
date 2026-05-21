from dataclasses import dataclass


@dataclass
class Slot:
    label: str = ""
    file: str = ""
    hotkey: str = ""
    color: str = "#1e2030"
    volume: float = 1.0
    favorite: bool = False
