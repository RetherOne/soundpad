import os

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.audio_engine import AudioEngine
from core.config import load_config, save_config
from core.enums import PlayerState
from ui.settings_panel import SettingsPanel
from ui.sound_card import SoundCard
from ui.titlebar import TitleBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._cfg = load_config()
        self._engine = AudioEngine()
        self._cards: list[SoundCard] = []
        self._active_card: SoundCard | None = None
        self._current_view = "all"  # "all" | "favorites"

        self.setWindowTitle("SoundPad")
        self.resize(1280, 820)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMinimumSize(900, 600)

        self._build_ui()
        self._build_cards()
        self._register_hotkeys()

        # Poll engine state to detect when a sound finishes naturally
        self._poll_timer = QTimer(self)
        self._poll_timer.setInterval(200)
        self._poll_timer.timeout.connect(self._poll_engine)
        self._poll_timer.start()

    # ── UI Construction ──────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._titlebar = TitleBar(self)
        root_layout.addWidget(self._titlebar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root_layout.addLayout(body)

        body.addWidget(self._build_sidebar())

        # ── Stacked content ──
        self._stack = QStackedWidget()
        body.addWidget(self._stack)

        self._sounds_page = self._build_sounds_page()
        self._stack.addWidget(self._sounds_page)  # index 0

        self._settings_page = SettingsPanel(self._engine, self._cfg)
        self._settings_page.engine_started.connect(self._on_engine_started)
        self._settings_page.engine_stopped.connect(self._on_engine_stopped)
        self._stack.addWidget(self._settings_page)  # index 1

        self._stack.setCurrentIndex(0)

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)

        sl = QVBoxLayout(sidebar)
        sl.setContentsMargins(12, 16, 12, 16)
        sl.setSpacing(4)

        nav_lbl = QLabel("LIBRARY")
        nav_lbl.setObjectName("SectionLabel")
        sl.addWidget(nav_lbl)
        sl.addSpacing(4)

        self._nav_all = QPushButton("  🎵  All Sounds")
        self._nav_all.setObjectName("GhostButtonActive")
        self._nav_all.clicked.connect(lambda: self._switch_view("all"))
        sl.addWidget(self._nav_all)

        self._nav_fav = QPushButton("  ♥  Favorites")
        self._nav_fav.setObjectName("GhostButton")
        self._nav_fav.clicked.connect(lambda: self._switch_view("favorites"))
        sl.addWidget(self._nav_fav)

        sl.addSpacing(12)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sl.addWidget(sep)
        sl.addSpacing(8)

        settings_lbl = QLabel("APP")
        settings_lbl.setObjectName("SectionLabel")
        sl.addWidget(settings_lbl)
        sl.addSpacing(4)

        self._nav_settings = QPushButton("  ⚙  Settings")
        self._nav_settings.setObjectName("GhostButton")
        self._nav_settings.clicked.connect(
            lambda: self._switch_view("settings")
        )
        sl.addWidget(self._nav_settings)

        sl.addStretch()

        # Engine status indicator
        self._sidebar_status = QLabel("● Engine off")
        self._sidebar_status.setObjectName("StatusRed")
        sl.addWidget(self._sidebar_status)

        # Sound count
        total = sum(1 for s in self._cfg["slots"] if s.get("file"))
        self._sound_count_lbl = QLabel(f"{total} sounds loaded")
        self._sound_count_lbl.setObjectName("Muted")
        sl.addWidget(self._sound_count_lbl)

        return sidebar

    def _build_sounds_page(self) -> QWidget:
        page = QWidget()
        pl = QVBoxLayout(page)
        pl.setContentsMargins(24, 20, 24, 20)
        pl.setSpacing(16)

        # ── Header ──
        hdr = QHBoxLayout()

        self._page_title = QLabel("Sound Library")
        self._page_title.setObjectName("Title")
        hdr.addWidget(self._page_title)
        hdr.addStretch()

        # Search box
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search sounds…")
        self._search.setFixedWidth(220)
        self._search.textChanged.connect(self._filter_cards)
        hdr.addWidget(self._search)

        # Global stop
        stop_all_btn = QPushButton("■  Stop All")
        stop_all_btn.setObjectName("StopBtn")
        stop_all_btn.setFixedWidth(110)
        stop_all_btn.clicked.connect(self._stop_all)
        hdr.addWidget(stop_all_btn)

        # Add sound
        add_btn = QPushButton("＋  Add Sound")
        add_btn.setFixedWidth(120)
        add_btn.clicked.connect(self._add_sound)
        hdr.addWidget(add_btn)

        pl.addLayout(hdr)

        # ── Scroll area ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        self._cards_container = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_container)
        self._cards_layout.setSpacing(10)
        self._cards_layout.addStretch()

        scroll.setWidget(self._cards_container)
        pl.addWidget(scroll)

        return page

    # ── Card management ─────────────────────────────────────────────

    def _build_cards(self):
        for card in self._cards:
            card.deleteLater()
        self._cards.clear()

        # Remove all items except the stretch
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, slot in enumerate(self._cfg["slots"]):
            if not slot.get("file") and not slot.get("label"):
                continue
            card = SoundCard(slot, i, self._engine)
            card.play_requested.connect(self._on_play_requested)
            card.stop_requested.connect(self._stop_all)
            card.favorite_toggled.connect(self._on_favorite_toggled)
            self._cards.append(card)
            self._cards_layout.insertWidget(
                self._cards_layout.count() - 1, card
            )

        # Update count
        total = sum(1 for s in self._cfg["slots"] if s.get("file"))
        self._sound_count_lbl.setText(f"{total} sounds loaded")

    def _add_sound(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Add Sounds",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.aac *.m4a)",
        )
        if not paths:
            return

        for path in paths:
            label = os.path.splitext(os.path.basename(path))[0]
            new_slot = {
                "label": label,
                "file": path,
                "hotkey": "",
                "color": "#1e2030",
                "volume": 1.0,
                "favorite": False,
            }
            # Find empty slot or append
            placed = False
            for i, slot in enumerate(self._cfg["slots"]):
                if not slot.get("file"):
                    self._cfg["slots"][i] = new_slot
                    placed = True
                    break
            if not placed:
                self._cfg["slots"].append(new_slot)

        save_config(self._cfg)
        self._build_cards()
        self._register_hotkeys()

    # ── Playback ────────────────────────────────────────────────────

    def _on_play_requested(self, filepath: str, volume: float):
        # Stop previous active card
        if self._active_card is not None:
            self._active_card.notify_stopped()

        # Find which card sent the signal
        sender_card = self.sender()
        self._active_card = sender_card

        if not self._engine.running:
            # Play without mic routing using simple playback
            self._engine.sfx_volume = volume
            self._engine.sfx_load_and_play(filepath)
        else:
            self._engine.sfx_volume = volume
            self._engine.sfx_load_and_play(filepath)

    def _stop_all(self):
        self._engine.sfx_stop()
        if self._active_card is not None:
            self._active_card.notify_stopped()
            self._active_card = None

    def _poll_engine(self):
        """Detect when a sound finishes naturally."""
        if (
            self._active_card is not None
            and self._engine.sfx_state == PlayerState.STOPPED
        ):
            self._active_card.notify_stopped()
            self._active_card = None

    # ── Filtering ───────────────────────────────────────────────────

    def _filter_cards(self, text: str):
        query = text.lower().strip()
        for card in self._cards:
            label = card._slot.get("label", "").lower()
            if self._current_view == "favorites":
                show = card._slot.get("favorite", False)
                if query:
                    show = show and query in label
            else:
                show = (not query) or (query in label)
            card.setVisible(show)

    def _switch_view(self, view: str):
        self._current_view = view

        # Reset nav buttons
        for btn, name in (
            (self._nav_all, "all"),
            (self._nav_fav, "favorites"),
            (self._nav_settings, "settings"),
        ):
            btn.setObjectName(
                "GhostButtonActive" if name == view else "GhostButton"
            )
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if view == "settings":
            self._stack.setCurrentIndex(1)
        else:
            self._stack.setCurrentIndex(0)
            if view == "favorites":
                self._page_title.setText("Favorites")
            else:
                self._page_title.setText("Sound Library")
            self._filter_cards(self._search.text())

    def _on_favorite_toggled(self, index: int, is_fav: bool):
        save_config(self._cfg)
        if self._current_view == "favorites":
            self._filter_cards(self._search.text())

    # ── Hotkeys ─────────────────────────────────────────────────────

    def _register_hotkeys(self):
        # Clear old shortcuts
        for sc in self.findChildren(QShortcut):
            sc.deleteLater()

        for card in self._cards:
            hotkey = card._slot.get("hotkey", "").strip()
            if hotkey:
                try:
                    sc = QShortcut(QKeySequence(hotkey), self)
                    sc.activated.connect(card.trigger_play)
                except Exception:
                    pass

    # ── Engine events ────────────────────────────────────────────────

    def _on_engine_started(self):
        self._sidebar_status.setText("● Engine running")
        self._sidebar_status.setObjectName("StatusGreen")
        self._sidebar_status.style().unpolish(self._sidebar_status)
        self._sidebar_status.style().polish(self._sidebar_status)

    def _on_engine_stopped(self):
        self._sidebar_status.setText("● Engine off")
        self._sidebar_status.setObjectName("StatusRed")
        self._sidebar_status.style().unpolish(self._sidebar_status)
        self._sidebar_status.style().polish(self._sidebar_status)

    # ── Window close ─────────────────────────────────────────────────

    def closeEvent(self, event):
        self._engine.stop()
        save_config(self._cfg)
        super().closeEvent(event)
