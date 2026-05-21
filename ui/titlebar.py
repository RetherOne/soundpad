from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
)


class TitleBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.setObjectName("TopBar")
        self.setFixedHeight(44)
        self.drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(6)

        logo = QLabel("SOUNDPAD")
        logo.setObjectName("LogoLabel")
        layout.addWidget(logo)
        layout.addStretch()

        # Версия / тег
        ver = QLabel("PRO")
        ver.setObjectName("HotkeyTag")
        layout.addWidget(ver)
        layout.addSpacing(12)

        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("⬜")
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("DangerButton")

        for btn in (self.min_btn, self.max_btn, self.close_btn):
            btn.setFixedSize(34, 28)
            layout.addWidget(btn)

        self.min_btn.clicked.connect(self._parent.showMinimized)
        self.max_btn.clicked.connect(self._toggle_max)
        self.close_btn.clicked.connect(self._parent.close)

    def _toggle_max(self):
        if self._parent.isMaximized():
            self._parent.showNormal()
            self.max_btn.setText("⬜")
        else:
            self._parent.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and not self._parent.isMaximized():
            delta = event.globalPosition().toPoint() - self.drag_pos
            self._parent.move(self._parent.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._toggle_max()
