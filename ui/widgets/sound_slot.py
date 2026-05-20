import tkinter as tk

from core.enums import PlayerState
from ui.styles import (
    ACCENT,
    BG3,
    BORDER,
    FONT_MAIN,
    FONT_MONO,
    FONT_TINY,
    TEXT,
    TEXT_DIM,
    WARNING,
)


class SoundSlot(tk.Frame):
    """Один слот: название + кнопки ▶ ⏸ ⏹ + редактирование."""

    def __init__(
        self, parent, index: int, slot: dict, engine, on_edit, on_play
    ):
        color = slot.get("color", "#1a2a1a")
        super().__init__(
            parent,
            bg=color,
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        self.index = index
        self.slot = slot
        self.engine = engine
        self.on_edit = on_edit
        self.on_play = on_play  # сообщить App что этот слот запущен

        # Состояние кнопок этого слота
        self._state = PlayerState.STOPPED  # STOPPED / PLAYING / PAUSED
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()

        slot = self.slot
        color = slot.get("color", "#1a2a1a")
        self.configure(bg=color)
        has_file = bool(slot.get("file"))

        # Горячая клавиша
        hk = slot.get("hotkey", "")
        if hk:
            tk.Label(self, text=hk, bg=color, fg=ACCENT, font=FONT_TINY).pack(
                anchor="ne", padx=4, pady=(3, 0)
            )

        # Название
        label = slot.get("label") or ("—" if not has_file else "?")
        tk.Label(
            self,
            text=label,
            bg=color,
            fg=TEXT if has_file else TEXT_DIM,
            font=FONT_MAIN,
            wraplength=110,
            justify="center",
        ).pack(expand=True)

        # Панель кнопок
        bf = tk.Frame(self, bg=color)
        bf.pack(fill="x", padx=4, pady=(0, 4))

        if has_file:
            # ▶/⏸ — один виджет, меняет надпись
            self._play_btn = tk.Button(
                bf,
                text="▶",
                width=2,
                bg=ACCENT,
                fg="#000",
                font=FONT_MONO,
                relief="flat",
                command=self._on_play_pause,
            )
            self._play_btn.pack(side="left", padx=(0, 2))

            # ⏹ — остановить и сбросить позицию
            tk.Button(
                bf,
                text="⏹",
                width=2,
                bg=BG3,
                fg=TEXT,
                font=FONT_MONO,
                relief="flat",
                command=self._on_stop,
            ).pack(side="left", padx=(0, 2))

        # Кнопка редактирования
        tk.Button(
            bf,
            text="✎",
            width=2,
            bg=BG3,
            fg=TEXT_DIM,
            font=FONT_TINY,
            relief="flat",
            command=lambda: self.on_edit(self.index),
        ).pack(side="right")

    # ── Обработчики кнопок ────────────────────────────────────────────────────

    def _on_play_pause(self):
        if self._state == PlayerState.STOPPED:
            # Сообщаем App — он остановит предыдущий активный слот
            self.on_play(self.index)
            self.engine.sfx_load_and_play(self.slot["file"])
            self._set_state(PlayerState.PLAYING)
        elif self._state == PlayerState.PLAYING:
            self.engine.sfx_pause()
            self._set_state(PlayerState.PAUSED)
        elif self._state == PlayerState.PAUSED:
            self.engine.sfx_pause()  # повторный вызов — resume
            self._set_state(PlayerState.PLAYING)

    def _on_stop(self):
        self.engine.sfx_stop()
        self._set_state(PlayerState.STOPPED)
        self.on_play(None)  # снять активный слот в App

    def force_stop(self):
        """Вызывается App когда другой слот начинает играть."""
        self._set_state(PlayerState.STOPPED)

    def notify_ended(self):
        """Вызывается App когда движок сообщает об окончании файла."""
        self._set_state(PlayerState.STOPPED)

    def _set_state(self, state: str):
        self._state = state
        color = self.slot.get("color", "#1a2a1a")
        if not hasattr(self, "_play_btn"):
            return
        if state == PlayerState.PLAYING:
            self._play_btn.configure(text="⏸", bg=WARNING, fg="#000")
            self.configure(
                bg=ACCENT if False else color
            )  # можно подсветить фон
        elif state == PlayerState.PAUSED:
            self._play_btn.configure(text="▶", bg=BG3, fg=WARNING)
        else:  # STOPPED
            self._play_btn.configure(text="▶", bg=ACCENT, fg="#000")

    def update_slot(self, slot: dict):
        self.slot = slot
        self._state = PlayerState.STOPPED
        self._build()

    # Публичный метод для горячей клавиши
    def trigger(self):
        self._on_play_pause()
