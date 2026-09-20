"""控制条：开始 / 暂停 / 单步 / 跳完 + 速度调节。实现 T5（issue #6）。

只发信号，不碰算法——具体动作由 MainWindow 接线（界面层契约）。
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QWidget

SPEED_MIN_MS = 80      # 最快：每拍 80ms
SPEED_MAX_MS = 1200    # 最慢：每拍 1200ms
SPEED_DEFAULT_MS = 400  # 契约默认 tick_ms


class ControlBar(QWidget):
    """顶部控制条。速度滑块单位为「每拍毫秒」，右移 = 更快。"""

    start_clicked = Signal()
    pause_toggled = Signal(bool)   # True = 已暂停
    step_clicked = Signal()
    finish_clicked = Signal()
    speed_changed = Signal(int)    # 每拍毫秒

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_btn = QPushButton("开始")
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setCheckable(True)
        self.step_btn = QPushButton("单步")
        self.finish_btn = QPushButton("跳完")

        self.speed = QSlider(Qt.Horizontal)
        self.speed.setRange(SPEED_MIN_MS, SPEED_MAX_MS)
        self.speed.setValue(SPEED_DEFAULT_MS)
        self.speed.setInvertedAppearance(True)  # 右移 = 毫秒更少 = 更快
        self.speed.setFixedWidth(160)
        self.speed_label = QLabel(self._speed_text(SPEED_DEFAULT_MS))
        self.speed_label.setFixedWidth(96)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.step_btn)
        layout.addWidget(self.finish_btn)
        layout.addStretch(1)
        layout.addWidget(QLabel("速度"))
        layout.addWidget(self.speed)
        layout.addWidget(self.speed_label)

        self.start_btn.clicked.connect(self.start_clicked)
        self.pause_btn.toggled.connect(self.pause_toggled)
        self.step_btn.clicked.connect(self.step_clicked)
        self.finish_btn.clicked.connect(self.finish_clicked)
        self.speed.valueChanged.connect(self._on_speed)

    # ---- 对外状态查询 ----

    def speed_ms(self) -> int:
        return self.speed.value()

    def set_running(self, running: bool) -> None:
        """演示进行中：禁用开始，放开暂停/单步/跳完。"""
        self.start_btn.setEnabled(not running)
        self.step_btn.setEnabled(running)
        self.finish_btn.setEnabled(running)
        if not running:
            self.pause_btn.setChecked(False)

    # ---- 内部 ----

    @staticmethod
    def _speed_text(ms: int) -> str:
        return f"{ms} ms/拍"

    def _on_speed(self, ms: int) -> None:
        self.speed_label.setText(self._speed_text(ms))
        self.speed_changed.emit(ms)
