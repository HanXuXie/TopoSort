# PR / 提交验收规范

> 目的：让“符合要求”可机械判定。PR 模板逐项勾选，CI 机器判定，组长只裁「不明确项」。
> 配套：AGENTS.md（红线）、evidence/decisions/2026-09-15-任务拆分总表.md（各任务 DoD）

## 一、两条流水线（PR 合并规则）

### 代码流（T2–T5、T6、T7 代码部分）
1. CI 必须绿：三平台矩阵（ubuntu/macos/windows）`uv sync && uv run pytest` 全过
2. 红测试转绿：对应模块的契约测试从红变绿（这是 T1 预埋的验收测试）
3. PR 模板逐项勾选（下方模板），空项 = 直接打回
4. 交叉评审 1 人通过（配对：models↔events、scene↔ui；契约/流程问题找组长）
5. 组长终审合并

### 文档流（T8 章节、T9 用例）
1. CI 中文档检查（组长 T1 里配好）：
   - 链接有效性（文档内引用的 evidence/ 文件必须真实存在）
   - 截图存在性：文档引用 `evidence/screenshots/...` 路径，脚本验证文件存在且 >20KB
   - md 语法 lint（markdownlint 规则集精简版）
2. 章节自检清单勾选
3. 组长终审（只裁结构完整性，不裁文笔）

## 二、通用 DoD（所有代码 PR 必须勾选）

```
## 自检清单（不勾满不提交）
- [ ] CI 绿（三平台矩阵全过）
- [ ] 新功能有行为测试（走公共 API + evidence/test-data 数据文件）
- [ ] 测试不 import 私有名称（下划线开头 / 模块内部函数）
- [ ] 无平台专属 API：路径用 pathlib、读写显式 encoding='utf-8'、写文件 newline=''
- [ ] 算法零 Qt：import app.models / app.events 后 sys.modules 无 PySide6（CI 已测）
- [ ] 材料：截图 ≥1 张入 evidence/screenshots/（命名 功能名-YYYYMMDD-N.png）
      或 benchmark 行 ≥1 条入 evidence/benchmarks.csv
      或 test-data 用例 ≥2 组
- [ ] 决策留档：本次实现中做出的所有小决定已记入 evidence/decisions/ 或关联 issue 留言
- [ ] 提交信息符合 `类型: 摘要` 格式
```

## 三、行为测试规则（违反 = 卡）

1. 只准通过公共 API（包 `__init__.py` 导出的名称）调用被测代码
2. 用例数据一律放 `evidence/test-data/NNN-描述.in/.expected`，测试代码读文件执行
3. 断言性质而非实现：输出序合法性、全集数量、事件流确定性、错误类型与行号
4. 禁止：访问 `_` 开头成员、断言内部调用次数/mocks 内部方法、依赖私有文件名或内部目录结构
5. 重构不改行为 → 测试必须全绿（PR 描述里注明“重构类提交”，CI 绿即可快速合）

## 四、按任务补充验收（在各 issue 里重复贴出）

- T2 算法：标准5节点图恰7序且全合法；max_count 截断；坏行报行号；30/60 节点极速模式 benchmark ≥2 行；零 Qt
- T3 事件：同输入两次播放事件序列逐项相等；标准图事件流恰7次 Complete；timeline 暂停/单步/恢复/上限K 行为测试；零 Qt
- T4 场景：pytest-qt offscreen 下喂脚本化事件后视觉状态断言；动画时长有界常量；PNG 导出非空；每类效果 ≥1 截图
- T5 界面：offscreen 全链路冒烟（粘贴→开始→结果）；文件往返；两类错误弹窗文案断言；主窗口各状态截图
- T6 联调：CI 全绿 + 中期演示彩排脚本通过（9.20）
- T7 打包：三份单文件产物（win 由 Actions 出）空目录启动冒烟 + SHA256 + readme.txt 三端说明
- T8 文档：对应章节含 evidence 引用、可通过文档检查、结构覆盖模板要求
- T9 用例：格式按契约、.in/.expected 成对、被 T2/T3 测试引用 ≥10 组、CSV ≥5 行

## 五、流程状态（issue 上打标签）

`认领`（加 assignee）→ 开发 → `in-review`（开 PR）→ 通过 → 合并关 issue
→ 不通过 → 打 `blocked` + 评论列整改清单 → 改完重新申请验收

## 六、CI 提供的机械判定（组长 T1 已建）

- `.github/workflows/ci.yml`：三平台矩阵测试 + 文档引用检查 + master 推送时自动打 Windows exe（artifact 下载，含 SHA256.txt）
- `app/tests/test_contracts.py`：零 Qt 红线、跨平台路径红线等机械断言，模块验收测试在此文件逐条预埋（红→绿）
- `tools/check_docs.py`：文档引用的 evidence/ 截图必须存在且 >20KB（防空图占位）
- 触发条件即验收标准：**PR 的 CI 红了，不需要任何理由，直接打回**
