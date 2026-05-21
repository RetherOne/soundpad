import json
import os

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".soundboard_config.json",
)
SOUNDS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sounds"
)
AUDIO_EXTS = {".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"}


def scan_sounds_dir() -> list[dict]:
    if not os.path.isdir(SOUNDS_DIR):
        return []
    files = sorted(
        f
        for f in os.listdir(SOUNDS_DIR)
        if os.path.splitext(f)[1].lower() in AUDIO_EXTS
    )
    slots = []
    for fname in files:
        slots.append(
            {
                "label": os.path.splitext(fname)[0],
                "file": os.path.join(SOUNDS_DIR, fname),
                "hotkey": "",
                "color": "#1e2030",
                "volume": 1.0,
                "favorite": False,
            }
        )
    return slots


def load_config():
    empty_slot = lambda: {
        "label": "",
        "file": "",
        "hotkey": "",
        "color": "#1e2030",
        "volume": 1.0,
        "favorite": False,
    }
    default = {
        "mic_device": None,
        "out_device": None,
        "monitor_device": None,
        "mic_volume": 1.0,
        "sfx_volume": 1.0,
        "slots": [empty_slot() for _ in range(24)],
    }

    def _autofill_from_sounds(slots: list[dict]) -> list[dict]:
        sound_slots = scan_sounds_dir()
        result = list(slots)
        sound_iter = iter(sound_slots)
        for i, slot in enumerate(result):
            if not slot.get("file"):
                try:
                    auto = next(sound_iter)
                    result[i] = auto
                except StopIteration:
                    break
        return result

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            while len(cfg.get("slots", [])) < 24:
                cfg.setdefault("slots", []).append(empty_slot())
            cfg["slots"] = _autofill_from_sounds(cfg["slots"])
            return cfg
        except Exception:
            pass

    default["slots"] = _autofill_from_sounds(default["slots"])
    return default


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
