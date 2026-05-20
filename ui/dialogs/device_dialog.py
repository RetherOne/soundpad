import tkinter as tk
from tkinter import ttk

from core.audio_engine import AudioEngine
from ui.styles import (
    ACCENT,
    BG2,
    FONT_BIG,
    FONT_MAIN,
    FONT_TINY,
    TEXT,
    WARNING,
)


class DeviceDialog(tk.Toplevel):
    def __init__(self, parent, engine: AudioEngine, cfg: dict, on_apply):
        super().__init__(parent)
        self.engine = engine
        self.cfg = cfg
        self.on_apply = on_apply
        self.title("Аудиоустройства")
        self.configure(bg=BG2)
        self.resizable(False, False)
        self.grab_set()

        inputs, outputs = AudioEngine.list_devices()
        in_names = [f"[{i}] {n}" for i, n in inputs]
        out_names = [f"[{i}] {n}" for i, n in outputs]
        self._in_ids = [i for i, _ in inputs]
        self._out_ids = [i for i, _ in outputs]
        pad = {"padx": 16, "pady": 8}

        def row(label, names, ids, current, r):
            tk.Label(self, text=label, bg=BG2, fg=TEXT, font=FONT_MAIN).grid(
                row=r, column=0, sticky="w", **pad
            )
            var = tk.StringVar()
            cb = ttk.Combobox(
                self,
                textvariable=var,
                values=names,
                state="readonly",
                width=40,
            )
            cb.grid(row=r, column=1, **pad)
            if current is not None:
                for j, idx in enumerate(ids):
                    if idx == current:
                        cb.current(j)
                        break
            return var

        self.mic_var = row(
            "🎤  Микрофон:", in_names, self._in_ids, cfg.get("mic_device"), 0
        )
        self.vbc_var = row(
            "🔌  VB-Cable Input:",
            out_names,
            self._out_ids,
            cfg.get("out_device"),
            1,
        )
        self.mon_var = row(
            "🎧  Мониторинг (себе):",
            out_names,
            self._out_ids,
            cfg.get("monitor_device"),
            2,
        )

        vbc_idx = AudioEngine.find_vbcable()
        hint = (
            f"VB-Cable найден: [{vbc_idx}]"
            if vbc_idx is not None
            else "VB-Cable не найден — установите с vb-audio.com/Cable"
        )
        hint_color = ACCENT if vbc_idx is not None else WARNING
        tk.Label(self, text=hint, bg=BG2, fg=hint_color, font=FONT_TINY).grid(
            row=3, column=0, columnspan=2, pady=4
        )

        tk.Button(
            self,
            text="Применить",
            bg=ACCENT,
            fg="#000",
            font=FONT_BIG,
            relief="flat",
            padx=20,
            command=self._apply,
        ).grid(row=4, column=0, columnspan=2, pady=12)

    def _get_id(self, var):
        sel = var.get()
        if not sel:
            return None
        try:
            return int(sel.split("]")[0].lstrip("["))
        except Exception:
            return None

    def _apply(self):
        self.cfg["mic_device"] = self._get_id(self.mic_var)
        self.cfg["out_device"] = self._get_id(self.vbc_var)
        self.cfg["monitor_device"] = self._get_id(self.mon_var)
        self.on_apply(self.cfg)
        self.destroy()
