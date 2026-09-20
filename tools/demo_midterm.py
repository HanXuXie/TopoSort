"""中期检查演示：真实引擎 + 真实渲染的标准图播放动画。

用法：
    uv run python tools/demo_midterm.py            # 弹窗播放（录屏用这个）
    QT_QPA_PLATFORM=offscreen uv run python ...    # 无界面自检模式

播完自动把最终画面存到 evidence/screenshots/，窗口自动关闭。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from app.events import Timeline, TopoPlayer
from app.models import parse
from app.scene import CandidatePool, GraphBoard

CANON_TEXT = "<A,C>\n<A,E>\n<B,C>\n<C,D>\n"
TICK_MS = 900  # 放慢节奏，方便录屏讲解


def main() -> None:
    app = QApplication.instance() or QApplication([])

    # 1) 真实解析 + 分层
    graph = parse(CANON_TEXT)
    layers = graph.layers()

    # 3) 渲染层（只认事件）
    timeline = Timeline(TopoPlayer(graph), tick_ms=TICK_MS)
    board = GraphBoard(graph.nodes, graph.edges, layers)
    pool = CandidatePool()

    header = QLabel(
        "TopoSort 中期演示 —— 输入: " + CANON_TEXT.replace("\n", " ")
        + "   |   事件流播放中…"
    )
    header.setStyleSheet("font-size: 16px; color: #e2e8f0; padding: 6px;")

    panel = QWidget()
    panel.setWindowTitle("TopoSort — 中期检查演示（T2 算法 / T3 事件流 / T4 渲染）")
    panel.setStyleSheet("background-color: #0f1726;")
    layout = QVBoxLayout(panel)
    layout.addWidget(header)
    layout.addWidget(pool)
    layout.addWidget(board)
    panel.resize(760, 720)
    panel.show()

    orders: list[tuple[str, ...]] = []

    def on_tick() -> None:
        events = timeline.tick()
        if not events:
            return
        for ev in events:
            board.apply_event(ev)
            kind = type(ev).__name__
            if kind == "Enqueue":
                pool.set_ready([ev.node])
            elif kind == "Consume":
                pool.on_consume(ev.node)
            elif kind == "Complete":
                orders.append(ev.order)
                print(f"[Complete] 分支{ev.branch_id}: {' → '.join(ev.order)}")
            elif kind in ("DeadEnd", "CycleFound"):
                print(f"[{kind}] {ev}")
        header.setText(
            f"拓扑序已找到 {len(orders)} / 7 条   |   "
            + " ".join("→".join(o) for o in orders[-1:])
        )
        if timeline.player.is_finished:
            timer.stop()
            out = PROJECT_ROOT / "evidence" / "screenshots" / "demo-final.png"
            board.export_png(out)
            print(f"共 {len(orders)} 条完整拓扑序，最终画面已存 {out.name}")
            QTimer.singleShot(1500, app.quit)

    timer = QTimer()
    timer.setInterval(TICK_MS)
    timer.timeout.connect(on_tick)
    timer.start()
    app.exec()


if __name__ == "__main__":
    main()
