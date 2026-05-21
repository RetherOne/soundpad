from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core.audio_engine import AudioEngine


class SettingsPanel(QWidget):
    engine_started = Signal()
    engine_stopped = Signal()

    def __init__(self, engine: AudioEngine, cfg: dict):
        super().__init__()
        self._engine = engine
        self._cfg = cfg
        self._build_ui()
        self._populate_devices()
        self._restore_from_config()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        title = QLabel("⚙  Settings")
        title.setObjectName("Title")
        root.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        root.addWidget(sep)

        # ── Audio Devices ──
        dev_lbl = QLabel("AUDIO DEVICES")
        dev_lbl.setObjectName("SectionLabel")
        root.addWidget(dev_lbl)

        def _row(label_text, combo):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(180)
            lbl.setObjectName("Muted")
            row.addWidget(lbl)
            row.addWidget(combo)
            return row

        self._mic_combo = QComboBox()
        self._out_combo = QComboBox()
        self._mon_combo = QComboBox()

        root.addLayout(_row("Microphone (input):", self._mic_combo))
        root.addLayout(_row("VB-Cable / Output:", self._out_combo))
        root.addLayout(_row("Monitor (headphones):", self._mon_combo))

        # ── Volume controls ──
        vol_lbl = QLabel("VOLUMES")
        vol_lbl.setObjectName("SectionLabel")
        root.addWidget(vol_lbl)

        def _vol_row(label_text, attr_name, init_val):
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setFixedWidth(180)
            lbl.setObjectName("Muted")
            row.addWidget(lbl)

            sl = QSlider(Qt.Horizontal)
            sl.setRange(0, 100)
            sl.setValue(int(init_val * 100))
            row.addWidget(sl)

            pct = QLabel(f"{sl.value()}%")
            pct.setFixedWidth(40)
            pct.setObjectName("Muted")
            pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row.addWidget(pct)

            sl.valueChanged.connect(lambda v, p=pct: p.setText(f"{v}%"))
            setattr(self, attr_name, sl)
            return row

        root.addLayout(
            _vol_row(
                "Microphone volume:",
                "_mic_vol",
                self._cfg.get("mic_volume", 1.0),
            )
        )
        root.addLayout(
            _vol_row(
                "SFX volume:", "_sfx_vol", self._cfg.get("sfx_volume", 1.0)
            )
        )

        # ── Sidetone ──
        self._sidetone_chk = QCheckBox(
            "  Sidetone (hear own mic in headphones)"
        )
        self._sidetone_chk.setStyleSheet("color: #8890aa;")
        root.addWidget(self._sidetone_chk)

        # ── Start / Stop engine ──
        btn_row = QHBoxLayout()

        self._start_btn = QPushButton("▶  Start Engine")
        self._start_btn.setObjectName("PlayBtn")
        self._start_btn.clicked.connect(self._start_engine)
        btn_row.addWidget(self._start_btn)

        self._stop_engine_btn = QPushButton("■  Stop Engine")
        self._stop_engine_btn.setObjectName("StopBtn")
        self._stop_engine_btn.setEnabled(False)
        self._stop_engine_btn.clicked.connect(self._stop_engine)
        btn_row.addWidget(self._stop_engine_btn)

        root.addLayout(btn_row)

        self._status_lbl = QLabel("● Engine stopped")
        self._status_lbl.setObjectName("StatusRed")
        root.addWidget(self._status_lbl)

        root.addStretch()

        # Слушаем изменения
        self._mic_vol.valueChanged.connect(self._apply_volumes)
        self._sfx_vol.valueChanged.connect(self._apply_volumes)
        self._sidetone_chk.toggled.connect(self._apply_sidetone)
        self._mic_combo.currentIndexChanged.connect(self._apply_devices)
        self._out_combo.currentIndexChanged.connect(self._apply_devices)
        self._mon_combo.currentIndexChanged.connect(self._apply_devices)

    def _populate_devices(self):
        inputs, outputs = AudioEngine.list_devices()

        self._mic_combo.addItem("— Select —", None)
        for idx, name in inputs:
            self._mic_combo.addItem(name, idx)

        for combo in (self._out_combo, self._mon_combo):
            combo.addItem("— None —", None)
            for idx, name in outputs:
                combo.addItem(name, idx)

    def _restore_from_config(self):
        def _set_combo(combo, saved_idx):
            for i in range(combo.count()):
                if combo.itemData(i) == saved_idx:
                    combo.setCurrentIndex(i)
                    return

        _set_combo(self._mic_combo, self._cfg.get("mic_device"))
        _set_combo(self._out_combo, self._cfg.get("out_device"))
        _set_combo(self._mon_combo, self._cfg.get("monitor_device"))

    def _apply_devices(self):
        self._engine.mic_device = self._mic_combo.currentData()
        self._engine.out_device = self._out_combo.currentData()
        self._engine.monitor_device = self._mon_combo.currentData()

        self._cfg["mic_device"] = self._engine.mic_device
        self._cfg["out_device"] = self._engine.out_device
        self._cfg["monitor_device"] = self._engine.monitor_device

    def _apply_volumes(self):
        mic_v = self._mic_vol.value() / 100.0
        sfx_v = self._sfx_vol.value() / 100.0
        self._engine.mic_volume = mic_v
        self._engine.sfx_volume = sfx_v
        self._cfg["mic_volume"] = mic_v
        self._cfg["sfx_volume"] = sfx_v

    def _apply_sidetone(self, checked: bool):
        self._engine.sidetone = checked

    def _start_engine(self):
        self._apply_devices()
        self._apply_volumes()
        try:
            self._engine.start()
            self._status_lbl.setText("● Engine running")
            self._status_lbl.setObjectName("StatusGreen")
            self._status_lbl.style().unpolish(self._status_lbl)
            self._status_lbl.style().polish(self._status_lbl)
            self._start_btn.setEnabled(False)
            self._stop_engine_btn.setEnabled(True)
            self.engine_started.emit()
        except RuntimeError as e:
            self._status_lbl.setText(f"⚠ {e}")

    def _stop_engine(self):
        self._engine.stop()
        self._status_lbl.setText("● Engine stopped")
        self._status_lbl.setObjectName("StatusRed")
        self._status_lbl.style().unpolish(self._status_lbl)
        self._status_lbl.style().polish(self._status_lbl)
        self._start_btn.setEnabled(True)
        self._stop_engine_btn.setEnabled(False)
        self.engine_stopped.emit()
