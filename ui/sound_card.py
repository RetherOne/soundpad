import os

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
)


class SoundCard(QFrame):
    """Fully functional sound card widget."""

    play_requested = Signal(str, float)  # filepath, volume
    stop_requested = Signal()
    favorite_toggled = Signal(int, bool)  # slot_index, is_favorite

    def __init__(self, slot_data: dict, slot_index: int, audio_engine=None):
        super().__init__()

        self._slot = slot_data
        self._index = slot_index
        self._engine = audio_engine
        self._is_playing = False
        self._is_active = False

        self.setObjectName("Card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(200)

        self._build_ui()
        self._update_favorite_btn()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(8)

        # ── Top row ──
        top = QHBoxLayout()
        top.setSpacing(8)

        label = self._slot.get("label") or "Empty Slot"
        self._title_lbl = QLabel(label)
        self._title_lbl.setStyleSheet(
            "font-size: 11pt; font-weight: 700; color: #c8cbdf;"
        )
        self._title_lbl.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        top.addWidget(self._title_lbl)

        # Hotkey badge
        hotkey = self._slot.get("hotkey", "")
        self._hotkey_lbl = QLabel(hotkey if hotkey else "—")
        self._hotkey_lbl.setObjectName("HotkeyTag")
        self._hotkey_lbl.setToolTip("Hotkey (click to assign)")
        top.addWidget(self._hotkey_lbl)

        # Favourite button
        self._fav_btn = QPushButton("♥")
        self._fav_btn.setObjectName("FavBtn")
        self._fav_btn.setFixedSize(30, 26)
        self._fav_btn.setToolTip("Add to favourites")
        self._fav_btn.clicked.connect(self._toggle_favorite)
        top.addWidget(self._fav_btn)

        root.addLayout(top)

        # ── Status row ──
        status_row = QHBoxLayout()
        status_row.setSpacing(8)

        # File name hint
        fname = os.path.basename(self._slot.get("file", "")) or "No file"
        self._status_lbl = QLabel(fname)
        self._status_lbl.setObjectName("Muted")
        self._status_lbl.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        status_row.addWidget(self._status_lbl)

        self._playing_lbl = QLabel("")
        self._playing_lbl.setObjectName("PlayingLabel")
        status_row.addWidget(self._playing_lbl)

        root.addLayout(status_row)

        # ── Volume slider ──
        vol_row = QHBoxLayout()
        vol_row.setSpacing(8)

        vol_icon = QLabel("🔊")
        vol_icon.setStyleSheet("font-size: 9pt; color: #505578;")
        vol_row.addWidget(vol_icon)

        self._vol_slider = QSlider(Qt.Horizontal)
        self._vol_slider.setRange(0, 100)
        self._vol_slider.setValue(int(self._slot.get("volume", 1.0) * 100))
        self._vol_slider.setToolTip("Volume")
        self._vol_slider.valueChanged.connect(self._on_volume_change)
        vol_row.addWidget(self._vol_slider)

        self._vol_pct = QLabel(f"{self._vol_slider.value()}%")
        self._vol_pct.setObjectName("Muted")
        self._vol_pct.setFixedWidth(36)
        self._vol_pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vol_row.addWidget(self._vol_pct)

        root.addLayout(vol_row)

        # ── Action buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        has_file = bool(self._slot.get("file"))

        self._play_btn = QPushButton("▶  PLAY")
        self._play_btn.setObjectName("PlayBtn")
        self._play_btn.setEnabled(has_file)
        self._play_btn.clicked.connect(self._on_play)
        btn_row.addWidget(self._play_btn)

        self._stop_btn = QPushButton("■  STOP")
        self._stop_btn.setObjectName("StopBtn")
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self._stop_btn)

        root.addLayout(btn_row)

        # ── Pulse timer for "playing" animation ──
        self._pulse_timer = QTimer(self)
        self._pulse_timer.setInterval(600)
        self._pulse_timer.timeout.connect(self._pulse)
        self._pulse_state = False

    # ── Slots ──

    def _on_play(self):
        filepath = self._slot.get("file", "")
        if not filepath or not os.path.exists(filepath):
            self._status_lbl.setText("⚠ File not found")
            return

        vol = self._vol_slider.value() / 100.0
        self.play_requested.emit(filepath, vol)
        self._set_playing(True)

    def _on_stop(self):
        self.stop_requested.emit()
        self._set_playing(False)

    def _on_volume_change(self, val: int):
        self._vol_pct.setText(f"{val}%")
        self._slot["volume"] = val / 100.0

    def _toggle_favorite(self):
        self._slot["favorite"] = not self._slot.get("favorite", False)
        self._update_favorite_btn()
        self.favorite_toggled.emit(self._index, self._slot["favorite"])

    def _update_favorite_btn(self):
        is_fav = self._slot.get("favorite", False)
        self._fav_btn.setObjectName("FavBtnActive" if is_fav else "FavBtn")
        self._fav_btn.setToolTip(
            "Remove from favourites" if is_fav else "Add to favourites"
        )
        # Force style refresh
        self._fav_btn.style().unpolish(self._fav_btn)
        self._fav_btn.style().polish(self._fav_btn)

    def _set_playing(self, playing: bool):
        self._is_playing = playing
        self._play_btn.setEnabled(not playing)
        self._stop_btn.setEnabled(playing)
        if playing:
            self._playing_lbl.setText("● PLAYING")
            self._pulse_timer.start()
            self.setObjectName("CardActive")
        else:
            self._playing_lbl.setText("")
            self._pulse_timer.stop()
            self.setObjectName("Card")
        # Refresh stylesheet
        self.style().unpolish(self)
        self.style().polish(self)

    def _pulse(self):
        self._pulse_state = not self._pulse_state
        if self._pulse_state:
            self._playing_lbl.setText("● PLAYING")
        else:
            self._playing_lbl.setText("  PLAYING")

    # ── Public API ──

    def notify_stopped(self):
        """Called by parent when audio engine finishes the track."""
        self._set_playing(False)

    def set_engine(self, engine):
        self._engine = engine

    def trigger_play(self):
        """Called by hotkey."""
        if self._is_playing:
            self._on_stop()
        else:
            self._on_play()
