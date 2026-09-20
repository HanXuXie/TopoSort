"""泳道面板：每条并行分支一行，实时显示该分支的推进。实现 T5（issue #6）。

只消费 StepEvent，不关心事件是怎么算出来的（渲染层契约）。
超出 lane_limit 的分支不建行，仅计入溢出提示（仍照常计数，见时间线契约）。
"""
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.events import (
    Complete,
    Consume,
    CycleFound,
    DeadEnd,
    Enqueue,
    Fork,
)

LANE_LIMIT = 8


class _LaneRow(QFrame):
    """单条泳道：分支号 + 该分支已消耗节点轨迹。"""

    def __init__(self, branch_id: int, parent=None):
        super().__init__(parent)
        self.branch_id = branch_id
        self.consumed: list[str] = []
        self.state = "idle"
        self.setFrameShape(QFrame.StyledPanel)

        self.name = QLabel(f"分支 {branch_id}")
        self.name.setFixedWidth(64)
        self.trace = QLabel("—")
        self.trace.setWordWrap(True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 6, 3)
        layout.addWidget(self.name)
        layout.addWidget(self.trace, 1)
        self._refresh()

    def mark_ready(self, node: str) -> None:
        self.state = "ready"
        self._refresh(suffix=f"就绪 [{node}]")

    def mark_consumed(self, node: str) -> None:
        if node not in self.consumed:
            self.consumed.append(node)
        self.state = "active"
        self._refresh()

    def mark_fork(self, node: str) -> None:
        self.state = "fork"
        self._refresh(suffix=f"分叉 → 选中 [{node}]")

    def mark_complete(self, order) -> None:
        self.consumed = list(order)
        self.state = "done"
        self._refresh()

    def mark_stuck(self, stuck_nodes) -> None:
        self.state = "stuck"
        self._refresh(suffix="[卡住] " + " ".join(sorted(stuck_nodes)))

    def _refresh(self, suffix: str = "") -> None:
        if self.state == "done":
            self.trace.setText("完成：" + " ".join(self.consumed))
        elif self.consumed:
            self.trace.setText(" → ".join(self.consumed) + (f"　{suffix}" if suffix else ""))
        else:
            self.trace.setText(suffix or "—")


class LanesPanel(QWidget):
    """右栏上半：泳道列表（滚动）。"""

    def __init__(self, parent=None, lane_limit: int = LANE_LIMIT):
        super().__init__(parent)
        self.lane_limit = lane_limit
        self._rows: dict[int, _LaneRow] = {}
        self._hidden: set[int] = set()

        self.overflow = QLabel("")
        self.overflow.setWordWrap(True)
        self.overflow.hide()

        self._host = QWidget()
        self._rows_layout = QVBoxLayout(self._host)
        self._rows_layout.setContentsMargins(2, 2, 2, 2)
        self._rows_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._host)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"泳道（分支并推，上限 {lane_limit}）"))
        layout.addWidget(scroll, 1)
        layout.addWidget(self.overflow)

    # ---- 对外 API ----

    def reset(self) -> None:
        for row in list(self._rows.values()):
            self._rows_layout.removeWidget(row)
            row.deleteLater()
        self._rows.clear()
        self._hidden.clear()
        self.overflow.hide()
        self.overflow.setText("")

    def lane_ids(self) -> list[int]:
        return sorted(self._rows)

    def lane_text(self, branch_id: int) -> str:
        row = self._rows.get(branch_id)
        return row.trace.text() if row else ""

    def on_event(self, event) -> None:
        if isinstance(event, CycleFound):
            for row in self._rows.values():
                row.mark_stuck(event.stuck_nodes)
            return
        branch_id = getattr(event, "branch_id", None)
        if branch_id is None:
            return
        if branch_id >= self.lane_limit:
            self._hidden.add(branch_id)
            self._refresh_overflow()
            return
        row = self._rows.get(branch_id) or self._new_row(branch_id)
        if isinstance(event, Enqueue):
            row.mark_ready(event.node)
        elif isinstance(event, Consume):
            row.mark_consumed(event.node)
        elif isinstance(event, Fork):
            row.mark_fork(event.node)
            if event.new_branch_id < self.lane_limit and event.new_branch_id not in self._rows:
                self._new_row(event.new_branch_id)
        elif isinstance(event, Complete):
            row.mark_complete(event.order)
        elif isinstance(event, DeadEnd):
            row.mark_stuck(event.stuck_nodes)

    # ---- 内部 ----

    def _new_row(self, branch_id: int) -> _LaneRow:
        row = _LaneRow(branch_id, self._host)
        self._rows[branch_id] = row
        self._rows_layout.insertWidget(self._rows_layout.count() - 1, row)
        return row

    def _refresh_overflow(self) -> None:
        n = len(self._hidden)
        self.overflow.setText(f"…另有 {n} 条分支超出泳道上限，不单独展示（仍计入结果）")
        self.overflow.show()
