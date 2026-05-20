import os
import tkinter as tk
from tkinter import filedialog

from ui.styles import (
    ACCENT,
    BG2,
    BG3,
    FONT_BIG,
    FONT_MAIN,
    FONT_MONO,
    FONT_TINY,
    SLOT_COLORS,
    TEXT,
)


class SlotEditor(tk.Toplevel):
    def __init__(self, parent, slot: dict, on_save):
        super().__init__(parent)
        self.slot = dict(slot)
        self.on_save = on_save
        self.title("Настройка звука")
        self.configure(bg=BG2)
        self.resizable(False, False)
        self.grab_set()
        pad = {"padx": 12, "pady": 6}

        tk.Label(self, text="Название:", bg=BG2, fg=TEXT, font=FONT_MAIN).grid(
            row=0, column=0, sticky="w", **pad
        )
        self.label_var = tk.StringVar(value=slot["label"])
        tk.Entry(
            self,
            textvariable=self.label_var,
            bg=BG3,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=FONT_MAIN,
            width=28,
        ).grid(row=0, column=1, **pad)

        tk.Label(self, text="Файл:", bg=BG2, fg=TEXT, font=FONT_MAIN).grid(
            row=1, column=0, sticky="w", **pad
        )
        self.file_var = tk.StringVar(value=slot["file"])
        ff = tk.Frame(self, bg=BG2)
        ff.grid(row=1, column=1, **pad, sticky="ew")
        tk.Entry(
            ff,
            textvariable=self.file_var,
            bg=BG3,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            font=FONT_TINY,
            width=22,
        ).pack(side="left")
        tk.Button(
            ff,
            text="…",
            bg=BG3,
            fg=ACCENT,
            relief="flat",
            command=self._browse,
            font=FONT_MAIN,
        ).pack(side="left", padx=4)

        tk.Label(
            self, text="Горячая клавиша:", bg=BG2, fg=TEXT, font=FONT_MAIN
        ).grid(row=2, column=0, sticky="w", **pad)
        self.hotkey_var = tk.StringVar(value=slot["hotkey"])
        hk = tk.Entry(
            self,
            textvariable=self.hotkey_var,
            bg=BG3,
            fg=ACCENT,
            insertbackground=ACCENT,
            relief="flat",
            font=FONT_MONO,
            width=12,
        )
        hk.grid(row=2, column=1, sticky="w", **pad)
        hk.bind("<KeyPress>", self._capture_key)

        tk.Label(self, text="Цвет:", bg=BG2, fg=TEXT, font=FONT_MAIN).grid(
            row=3, column=0, sticky="w", **pad
        )
        cf = tk.Frame(self, bg=BG2)
        cf.grid(row=3, column=1, sticky="w", **pad)
        for c in SLOT_COLORS:
            tk.Button(
                cf,
                bg=c,
                width=2,
                relief="flat",
                command=lambda x=c: self._pick_color(x),
            ).pack(side="left", padx=2)

        bf = tk.Frame(self, bg=BG2)
        bf.grid(row=4, column=0, columnspan=2, pady=12)
        tk.Button(
            bf,
            text="Сохранить",
            bg=ACCENT,
            fg="#000",
            font=FONT_BIG,
            relief="flat",
            padx=16,
            command=self._save,
        ).pack(side="left", padx=8)
        tk.Button(
            bf,
            text="Отмена",
            bg=BG3,
            fg=TEXT,
            font=FONT_MAIN,
            relief="flat",
            padx=16,
            command=self.destroy,
        ).pack(side="left")

    def _browse(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Audio", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a"),
                ("All", "*.*"),
            ]
        )
        if path:
            self.file_var.set(path)
            if not self.label_var.get():
                self.label_var.set(os.path.splitext(os.path.basename(path))[0])

    def _capture_key(self, event):
        if event.keysym not in (
            "Shift_L",
            "Shift_R",
            "Control_L",
            "Control_R",
            "Alt_L",
            "Alt_R",
        ):
            self.hotkey_var.set(event.keysym.upper())
        return "break"

    def _pick_color(self, color):
        self.slot["color"] = color

    def _save(self):
        self.slot["label"] = self.label_var.get().strip()
        self.slot["file"] = self.file_var.get().strip()
        self.slot["hotkey"] = self.hotkey_var.get().strip()
        self.on_save(self.slot)
        self.destroy()
