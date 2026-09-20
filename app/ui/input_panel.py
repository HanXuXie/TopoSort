"""输入面板：关系文本编辑 + 打开 / 保存。实现 T5（issue #6）。

跨平台红线：路径用 pathlib，读写显式 UTF-8，写文件 newline=''。
"""
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

FILE_FILTER = "关系文本 (*.in *.txt);;所有文件 (*)"
PLACEHOLDER = "<A,C>\n<A,E>\n<B,C>\n<C,D>"


class InputPanel(QWidget):
    """左栏：多行输入框 + 打开/保存按钮。文件对话框由 MainWindow 弹。"""

    open_requested = Signal()
    save_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        title = QLabel("输入：每行一条先修关系")
        hint = QLabel("<A,C> 表示 A 必须先于 C；空白行自动跳过")

        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText(PLACEHOLDER)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)

        self.open_btn = QPushButton("打开…")
        self.save_btn = QPushButton("保存…")
        self.clear_btn = QPushButton("清空")
        buttons = QHBoxLayout()
        buttons.addWidget(self.open_btn)
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.clear_btn)
        buttons.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(hint)
        layout.addWidget(self.editor, 1)
        layout.addLayout(buttons)

        self.open_btn.clicked.connect(self.open_requested)
        self.save_btn.clicked.connect(self.save_requested)
        self.clear_btn.clicked.connect(self.clear)

    # ---- 对外 API ----

    def set_text(self, text: str) -> None:
        self.editor.setPlainText(text)

    def text(self) -> str:
        return self.editor.toPlainText()

    def clear(self) -> None:
        self.set_text("")

    def save_to(self, path: Path) -> None:
        """写 UTF-8，newline='' 保证三端换行不被偷换。"""
        Path(path).write_text(self.text(), encoding="utf-8", newline="")

    def load_from(self, path: Path) -> None:
        self.set_text(Path(path).read_text(encoding="utf-8"))
