APP_STYLE = """
 
/* ── Base ── */
QWidget {
    background-color: #0d0e11;
    color: #e2e4ea;
    font-family: 'Segoe UI', 'SF Pro Display', sans-serif;
    font-size: 10pt;
}
 
QMainWindow {
    background-color: #0d0e11;
}
 
/* ── Scrollbars ── */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2e3140;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #3d4260;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: none; }
 
QScrollArea {
    border: none;
    background: transparent;
}
 
/* ── Sidebar ── */
QFrame#Sidebar {
    background-color: #11131a;
    border-right: 1px solid #1e2030;
}
 
/* ── Top Bar ── */
QFrame#TopBar {
    background-color: #11131a;
    border-bottom: 1px solid #1e2030;
}
 
/* ── Sound Card ── */
QFrame#Card {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #181b26, stop:1 #13151f);
    border: 1px solid #232638;
    border-radius: 10px;
}
QFrame#Card:hover {
    border: 1px solid #4a5080;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1d2033, stop:1 #161826);
}
QFrame#CardActive {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a2a40, stop:1 #111d30);
    border: 1px solid #3a7bd5;
    border-radius: 10px;
}
 
/* ── Buttons ── */
QPushButton {
    background-color: #252840;
    border: 1px solid #323660;
    border-radius: 7px;
    padding: 7px 14px;
    color: #c8cbdf;
    font-weight: 600;
    font-size: 9pt;
}
QPushButton:hover {
    background-color: #2e3255;
    border-color: #4a5090;
    color: #e8eaf8;
}
QPushButton:pressed {
    background-color: #1e2240;
}
 
QPushButton#PlayBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2c5f9e, stop:1 #1e4a80);
    border: 1px solid #3a70b8;
    color: #d0e8ff;
}
QPushButton#PlayBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3a72b8, stop:1 #2a5c99);
    border-color: #5090d8;
}
QPushButton#PlayBtn:pressed {
    background: #1a3e70;
}
 
QPushButton#StopBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7a2020, stop:1 #601818);
    border: 1px solid #963030;
    color: #ffc8c8;
}
QPushButton#StopBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #9a2828, stop:1 #7a2020);
    border-color: #c04040;
}
QPushButton#StopBtn:pressed {
    background: #501010;
}
 
QPushButton#FavBtn {
    background: transparent;
    border: 1px solid #2a2d45;
    border-radius: 6px;
    padding: 4px 8px;
    color: #555880;
    font-size: 13pt;
}
QPushButton#FavBtn:hover {
    background: #1e2035;
    color: #f0a030;
    border-color: #555;
}
QPushButton#FavBtnActive {
    background: transparent;
    border: 1px solid #6a5010;
    border-radius: 6px;
    padding: 4px 8px;
    color: #f0a030;
    font-size: 13pt;
}
QPushButton#FavBtnActive:hover {
    color: #ffb840;
}
 
QPushButton#GhostButton {
    background: transparent;
    border: none;
    color: #8890aa;
    text-align: left;
    padding: 8px 12px;
    font-size: 10pt;
}
QPushButton#GhostButton:hover {
    background-color: #1a1d2a;
    color: #d0d4e8;
    border-radius: 8px;
}
QPushButton#GhostButtonActive {
    background: #1a1d2a;
    border: none;
    border-left: 2px solid #4a7dd8;
    color: #d0d4e8;
    text-align: left;
    padding: 8px 12px;
    font-size: 10pt;
    border-radius: 0px;
}
 
QPushButton#DangerButton {
    background: transparent;
    border: none;
    color: #8890aa;
}
QPushButton#DangerButton:hover {
    background: #3a1515;
    color: #ff6060;
    border-radius: 6px;
}
 
QPushButton#AddSoundBtn {
    background: transparent;
    border: 1px dashed #2e3255;
    border-radius: 10px;
    color: #4a5080;
    font-size: 11pt;
    padding: 16px;
}
QPushButton#AddSoundBtn:hover {
    border-color: #4a5090;
    color: #8090c0;
    background: #141628;
}
 
/* ── Sliders ── */
QSlider::groove:horizontal {
    height: 4px;
    background: #1e2030;
    border-radius: 2px;
}
QSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #2c5f9e, stop:1 #4a90d9);
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #d0e0ff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
    border: 2px solid #3a70b8;
}
QSlider::handle:horizontal:hover {
    background: #ffffff;
}
 
/* ── Labels ── */
QLabel#Title {
    font-size: 15pt;
    font-weight: 700;
    color: #d8daf0;
    letter-spacing: 1px;
}
QLabel#LogoLabel {
    font-size: 13pt;
    font-weight: 800;
    color: #d0d4f8;
    letter-spacing: 3px;
}
QLabel#SectionLabel {
    font-size: 8pt;
    font-weight: 700;
    color: #484d70;
    letter-spacing: 2px;
}
QLabel#Muted {
    color: #464b6a;
    font-size: 9pt;
}
QLabel#StatusGreen {
    color: #3ab870;
    font-weight: 700;
    font-size: 9pt;
}
QLabel#StatusRed {
    color: #d04040;
    font-weight: 700;
    font-size: 9pt;
}
QLabel#HotkeyTag {
    background: #1c1f30;
    color: #5060a0;
    border: 1px solid #2a2e48;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 8pt;
    font-family: 'Consolas', monospace;
}
QLabel#PlayingLabel {
    color: #4a90d9;
    font-weight: 700;
    font-size: 9pt;
}
 
/* ── ComboBox ── */
QComboBox {
    background: #141628;
    border: 1px solid #2a2e48;
    border-radius: 7px;
    padding: 5px 10px;
    color: #c0c4e0;
    min-width: 180px;
}
QComboBox:hover {
    border-color: #4a5090;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    background: #141628;
    border: 1px solid #2a2e48;
    selection-background-color: #252840;
    color: #c0c4e0;
    outline: none;
}
 
/* ── Line Edit ── */
QLineEdit {
    background: #141628;
    border: 1px solid #2a2e48;
    border-radius: 7px;
    padding: 5px 10px;
    color: #c0c4e0;
}
QLineEdit:focus {
    border-color: #3a70b8;
}
 
/* ── Tool Tip ── */
QToolTip {
    background: #1a1d2e;
    color: #c8cbdf;
    border: 1px solid #3a3d58;
    padding: 4px 8px;
    border-radius: 4px;
}
 
/* ── Separator ── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    background: #1e2030;
    max-height: 1px;
    border: none;
}
 
"""
