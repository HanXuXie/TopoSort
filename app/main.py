"""程序入口：装配 ui.run()。实现 T5（issue #6）。"""

import sys
from pathlib import Path

# 兼容 `uv run python app/main.py` 直启方式：把项目根加进导入路径，
# 否则按文件路径运行时 Python 找不到 app 包（uv run python -m app.main 不受影响）。
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui import run  # noqa: E402

run()
