import tkinter as tk
from tkinter import messagebox

from core.audio_engine import AudioEngine
from core.config import SOUNDS_DIR, load_config, save_config, scan_sounds_dir
from core.enums import PlayerState
from ui.dialogs.device_dialog import DeviceDialog
from ui.dialogs.slot_editor import SlotEditor
from ui.styles import (
    ACCENT,
    BG,
    BG3,
    BORDER,
    DANGER,
    FONT_BIG,
    FONT_MAIN,
    FONT_MONO,
    FONT_TINY,
    TEXT,
    TEXT_DIM,
    WARNING,
)
from ui.widgets.sound_slot import SoundSlot


class App(tk.Tk):
    ROWS = 4
    COLS = 6
    POLL_MS = 80  # как часто опрашиваем движок для обновления GUI

    def __init__(self):
        super().__init__()
        self.title("SoundBoard")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.minsize(760, 520)

        self.cfg = load_config()
        self.engine = AudioEngine()
        self.engine.on_sfx_state = None  # используем polling
        self._active_slot: int | None = None  # индекс играющего слота
        self._apply_cfg()
        self._build_ui()
        self._register_hotkeys()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._poll_engine()  # запускаем периодический опрос

    def _apply_cfg(self):
        self.engine.mic_device = self.cfg.get("mic_device")
        self.engine.out_device = self.cfg.get("out_device")
        self.engine.monitor_device = self.cfg.get("monitor_device")
        self.engine.mic_volume = self.cfg.get("mic_volume", 1.0)
        self.engine.sfx_volume = self.cfg.get("sfx_volume", 1.0)

    # ── Периодический опрос движка ────────────────────────────────────────────

    def _poll_engine(self):
        """Каждые POLL_MS мс проверяем: не закончился ли трек."""
        if self._active_slot is not None:
            with self.engine._sfx_lock:
                state = self.engine._sfx_state
            if state == PlayerState.STOPPED:
                slot_ui = self._slots_ui[self._active_slot]
                slot_ui.notify_ended()
                self._active_slot = None
        self.after(self.POLL_MS, self._poll_engine)

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Шапка
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=16, pady=(12, 6))

        tk.Label(
            header,
            text="SOUNDBOARD",
            bg=BG,
            fg=ACCENT,
            font=("Consolas", 18, "bold"),
        ).pack(side="left")

        self._status_var = tk.StringVar(value="● ОСТАНОВЛЕН")
        self._status_lbl = tk.Label(
            header,
            textvariable=self._status_var,
            bg=BG,
            fg=DANGER,
            font=FONT_MONO,
        )
        self._status_lbl.pack(side="left", padx=20)

        ctrl = tk.Frame(header, bg=BG)
        ctrl.pack(side="right")

        self._start_btn = tk.Button(
            ctrl,
            text="▶  СТАРТ",
            bg=ACCENT,
            fg="#000",
            font=FONT_BIG,
            relief="flat",
            padx=14,
            command=self._toggle_stream,
        )
        self._start_btn.pack(side="left", padx=4)

        tk.Button(
            ctrl,
            text="⚙  УСТРОЙСТВА",
            bg=BG3,
            fg=TEXT,
            font=FONT_MAIN,
            relief="flat",
            padx=10,
            command=self._open_devices,
        ).pack(side="left", padx=4)

        tk.Button(
            ctrl,
            text="↺  SOUNDS",
            bg=BG3,
            fg=ACCENT,
            font=FONT_MAIN,
            relief="flat",
            padx=10,
            command=self._reload_sounds,
        ).pack(side="left", padx=4)

        # Громкость
        vol_frame = tk.Frame(self, bg=BG)
        vol_frame.pack(fill="x", padx=16, pady=(0, 10))

        self._make_slider(
            vol_frame,
            "🎤 Микрофон",
            self.cfg.get("mic_volume", 1.0),
            lambda v: setattr(self.engine, "mic_volume", float(v)),
        )
        self._make_slider(
            vol_frame,
            "🔊 Звуки",
            self.cfg.get("sfx_volume", 1.0),
            lambda v: setattr(self.engine, "sfx_volume", float(v)),
        )

        self._mute_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            vol_frame,
            text="МУТ MIC",
            variable=self._mute_var,
            bg=BG,
            fg=WARNING,
            selectcolor=BG3,
            font=FONT_MONO,
            command=lambda: setattr(
                self.engine, "mic_muted", self._mute_var.get()
            ),
        ).pack(side="left", padx=16)

        self._sidetone_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            vol_frame,
            text="🎧 СЛЫШАТЬ СЕБЯ",
            variable=self._sidetone_var,
            bg=BG,
            fg=TEXT_DIM,
            selectcolor=BG3,
            font=FONT_MONO,
            command=lambda: setattr(
                self.engine, "sidetone", self._sidetone_var.get()
            ),
        ).pack(side="left", padx=8)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=16, pady=4)

        # Сетка слотов
        grid = tk.Frame(self, bg=BG)
        grid.pack(fill="both", expand=True, padx=16, pady=8)

        self._slots_ui: list[SoundSlot] = []
        for r in range(self.ROWS):
            grid.rowconfigure(r, weight=1)
            for c in range(self.COLS):
                grid.columnconfigure(c, weight=1)
                idx = r * self.COLS + c
                w = SoundSlot(
                    grid,
                    idx,
                    self.cfg["slots"][idx],
                    self.engine,
                    on_edit=self._edit_slot,
                    on_play=self._on_slot_play,
                )
                w.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
                self._slots_ui.append(w)

        tk.Label(
            self,
            text="Горячие клавиши работают когда окно в фокусе",
            bg=BG,
            fg=TEXT_DIM,
            font=FONT_TINY,
        ).pack(pady=(4, 8))

    def _make_slider(self, parent, label, init, cmd):
        f = tk.Frame(parent, bg=BG)
        f.pack(side="left", padx=8)
        tk.Label(f, text=label, bg=BG, fg=TEXT_DIM, font=FONT_TINY).pack(
            side="left"
        )
        s = tk.Scale(
            f,
            from_=0,
            to=2,
            resolution=0.05,
            orient="horizontal",
            length=140,
            bg=BG,
            fg=TEXT,
            troughcolor=BG3,
            highlightthickness=0,
            showvalue=False,
            command=cmd,
        )
        s.set(init)
        s.pack(side="left", padx=4)

    # ── Логика ────────────────────────────────────────────────────────────────

    def _on_slot_play(self, index: int | None):
        """Вызывается слотом при нажатии ▶. Останавливает предыдущий активный."""
        if self._active_slot is not None and self._active_slot != index:
            self._slots_ui[self._active_slot].force_stop()
        self._active_slot = index

    def _toggle_stream(self):
        if self.engine.running:
            self.engine.stop()
            self._start_btn.configure(text="▶  СТАРТ", bg=ACCENT, fg="#000")
            self._status_var.set("● ОСТАНОВЛЕН")
            self._status_lbl.configure(fg=DANGER)
        else:
            try:
                self.engine.start()
                self._start_btn.configure(
                    text="⏸  ПАУЗА", bg=WARNING, fg="#000"
                )
                self._status_var.set("● АКТИВЕН")
                self._status_lbl.configure(fg=ACCENT)
            except RuntimeError as e:
                messagebox.showerror("Ошибка", str(e))

    def _open_devices(self):
        DeviceDialog(self, self.engine, self.cfg, self._on_devices_applied)

    def _on_devices_applied(self, new_cfg):
        self.cfg.update(new_cfg)
        was = self.engine.running
        if was:
            self.engine.stop()
        self._apply_cfg()
        if was:
            try:
                self.engine.start()
            except RuntimeError as e:
                messagebox.showerror("Ошибка", str(e))
        save_config(self.cfg)

    def _edit_slot(self, index: int):
        def on_save(new_slot):
            self.cfg["slots"][index] = new_slot
            self._slots_ui[index].update_slot(new_slot)
            self._register_hotkeys()
            save_config(self.cfg)

        SlotEditor(self, self.cfg["slots"][index], on_save)

    def _reload_sounds(self):
        """Пересканировать папку sounds и заполнить пустые слоты."""
        sound_slots = scan_sounds_dir()
        if not sound_slots:
            messagebox.showinfo(
                "Папка sounds", f"Аудиофайлы не найдены.{SOUNDS_DIR}"
            )
            return
        sound_iter = iter(sound_slots)
        changed = 0
        for i, slot in enumerate(self.cfg["slots"]):
            if not slot.get("file"):
                try:
                    auto = next(sound_iter)
                    self.cfg["slots"][i] = auto
                    self._slots_ui[i].update_slot(auto)
                    changed += 1
                except StopIteration:
                    break
        self._register_hotkeys()
        save_config(self.cfg)
        if changed:
            messagebox.showinfo(
                "Sounds", f"Добавлено {changed} звук(ов) из папки sounds."
            )
        else:
            messagebox.showinfo(
                "Sounds", "Все слоты уже заняты или новых файлов нет."
            )

    def _register_hotkeys(self):
        self._hotkeys = {}
        for i, slot in enumerate(self.cfg["slots"]):
            hk = slot.get("hotkey", "").strip()
            if hk and slot.get("file"):
                self._hotkeys[hk.upper()] = i
                self.bind(
                    f"<KeyPress-{hk}>",
                    lambda e, idx=i: self._slots_ui[idx].trigger(),
                )

    def _on_close(self):
        self.engine.stop()
        self.cfg["mic_volume"] = self.engine.mic_volume
        self.cfg["sfx_volume"] = self.engine.sfx_volume
        save_config(self.cfg)
        self.destroy()
