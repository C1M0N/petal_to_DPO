#!/usr/bin/env python3
"""Build ch02 notebooks (+ generic template) from this single source of truth.

Re-run after edits:
    cd blossom && python scripts/build.py

Outputs:
    templates/_chapter_template.ipynb
    ch02-linear-algebra/ch02.ipynb       (demo, 含完整答案；生成后**只读**)
    ch02-linear-algebra/ch02_work.ipynb  (work, 填空版；生成后**只读**)

学生工作流：
    生成的 .ipynb 都是只读「教材副本」。要做题请运行：
        python scripts/new_attempt.py ch02
    会复制一份可写的 ch02-linear-algebra/ch02_attempt.ipynb 给你做。
"""

import json
import os
import platform
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
IS_MACOS = platform.system() == "Darwin"


def _lock_macos(path: Path):
    """macOS: 用 chflags uchg 给文件加 user-immutable 标志。
    加完后即使 owner 也不能修改（VS Code 也救不了），除非先 chflags nouchg。
    """
    if IS_MACOS:
        subprocess.run(["chflags", "uchg", str(path)], check=False)


def _unlock_macos(path: Path):
    """macOS: 移除 user-immutable 标志，让文件可写。rebuild 时必须先调这个。"""
    if IS_MACOS:
        subprocess.run(["chflags", "nouchg", str(path)], check=False)


# =========================================================
# Cell helpers
# =========================================================

def _md(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def _code(source):
    return {"cell_type": "code", "metadata": {}, "source": source,
            "execution_count": None, "outputs": []}


def write_ipynb(cells, rel_path, readonly=True):
    """生成 .ipynb 文件，默认设为只读（防学生直接改教材副本）。

    要做题学生应跑 `scripts/new_attempt.py` 复制可写副本。
    rebuild 时若文件已存在为只读，会先解除只读再写入。
    """
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
                "mimetype": "text/x-python",
                "file_extension": ".py",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out = ROOT / rel_path
    out.parent.mkdir(parents=True, exist_ok=True)
    # 若已存在只读/uchg 文件，先解锁才能写入
    if out.exists():
        _unlock_macos(out)  # 解除 user-immutable
        os.chmod(out, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    if readonly:
        # 双重锁：chmod 444 + macOS chflags uchg
        # 后者让 VS Code 完全无法保存（不只是弹框），真正达到「教材副本不可改」
        os.chmod(out, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
        _lock_macos(out)
        ro_tag = " [只读 + uchg]" if IS_MACOS else " [只读]"
    else:
        ro_tag = ""
    print(f"  wrote {out.relative_to(ROOT)} ({len(cells)} cells){ro_tag}")


class Builder:
    """累计 demo + work 副本两套 cells。"""

    def __init__(self):
        self.demo = []
        self.work = []

    def md(self, source):
        c = _md(source)
        self.demo.append(c)
        self.work.append(c)

    def code(self, demo_src, work_src=None):
        self.demo.append(_code(demo_src))
        self.work.append(_code(demo_src if work_src is None else work_src))


def _yuanwen(b: Builder, title: str, md_body: str, code_body: str = None):
    """嵌入花书原文（朱明超精读版花书第 2 章）的一节，作为 #### 📖 callout。

    放在对应 blossom 小节之前，作为「**先看原文怎么定义，再看 blossom 怎么展开**」的底本。

    source: 花书拆解/重要章节/2 线性代数.pdf
    """
    b.md(f"#### 📖 花书原文 — {title}\n\n{md_body}")
    if code_body:
        b.code(code_body)


# =========================================================
# Template (通用 7 段骨架)
# =========================================================

def build_template():
    cells = []
    cells.append(_md(
        "# 第 X 章：<标题>\n\n"
        "> Demo 副本。学习时打开 work 副本边读边填。\n\n"
        "## 配套资料\n\n"
        "- 📖 花书 PDF：`30 The Colonnade/36 Library/花书.pdf`\n"
        "- 📝 阅读笔记：`花书笔记.md`\n"
        "- 🔗 相关 notio：（按需补 obsidian:// URI）\n\n"
        "## 本章导航\n\n"
        "| Sec | 主题 |\n|-----|------|\n"
        "| 0 | Jupyter 速查 + 环境 |\n"
        "| 1 | 直觉 |\n"
        "| 2 | 形式化定义 |\n"
        "| 3 | NumPy 手写 |\n"
        "| 4 | 可视化 |\n"
        "| 5 | 与花书对照 |\n"
        "| 6 | 综合练习 |\n"
        "| 7 | 自由探索 |\n"
        "| CHECKPOINT | 自检清单 |\n"
    ))
    cells.append(_md("## Sec 0 — Jupyter 速查 + 环境\n\n（首章详讲；后续章节简提）"))
    cells.append(_code(
        "import sys\nsys.path.insert(0, '..')\n"
        "import numpy as np\nimport matplotlib.pyplot as plt\n"
        "from utils import checks, viz"
    ))
    cells.append(_md("## Sec 1 — 直觉先行\n\n（用自己的话+几何/类比导入本章核心概念）"))
    cells.append(_md("### ✏️ 例题 1.x\n\n描述...\n"))
    cells.append(_code("# 例题代码\npass"))
    cells.append(_md("## Sec 2 — 形式化定义\n\n（精确数学定义）"))
    cells.append(_md("## Sec 3 — NumPy 手写\n\n（每个算子：原理 → 手写 → 与 `np.linalg.*` 对照）"))
    cells.append(_md("## Sec 4 — 可视化\n\n（matplotlib + 少量 ipywidgets）"))
    cells.append(_md("## Sec 5 — 与花书对照\n\n（短引用花书定义 < 15 词 + 复述 + 链回 vault notio）"))
    cells.append(_md("## Sec 6 — 综合练习\n\n（跨节大题）"))
    cells.append(_md("## Sec 7 — 自由探索\n\n（开放任务）"))
    cells.append(_md(
        "## CHECKPOINT — 本章自检\n\n"
        "- [ ] 能用自己的话说清核心概念\n"
        "- [ ] 能手写 NumPy 实现\n"
        "- [ ] 完成所有填空与 YOUR TURN\n"
        "- [ ] 至少 1 个自由探索做出来\n"
    ))
    cells.append(_code("from utils import checks\nchecks.report()"))
    write_ipynb(cells, "templates/_chapter_template.ipynb")


# =========================================================
# Ch 2: 线性代数 — 各 section 装填
# =========================================================

def ch02_header(b: Builder):
    b.md(
        "# 花书 · 第二章：线性代数\n\n"
        "> 你正打开的是 demo / work 副本。**学习时用 work 副本**，把空 `___` 处填上代码，看 ✅ 验证。\n\n"
        "## 配套资料\n\n"
        "- 📖 花书 PDF（vault）：`30 The Colonnade/36 Library/花书.pdf`\n"
        "- 📝 阅读笔记：`花书笔记.md`\n"
        "- 🔗 vault notio（点击在 Obsidian 打开）：\n"
        "  - [张量](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E5%BC%A0%E9%87%8F)\n"
        "  - [矩阵乘法](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E7%9F%A9%E9%98%B5%E4%B9%98%E6%B3%95)\n"
        "  - [Hadamard 乘积](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2FHadamard%20%E4%B9%98%E7%A7%AF)\n"
        "  - [Einstein 求和约定](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2FEinstein%20%E6%B1%82%E5%92%8C%E7%BA%A6%E5%AE%9A)\n"
        "  - [张量语言](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E5%BC%A0%E9%87%8F%E8%AF%AD%E8%A8%80)\n\n"
        "## 本章导航\n\n"
        "| Sec | 主题 | 例题数 |\n"
        "|-----|------|------|\n"
        "| 0 | Jupyter 入门 + 环境 | 4 |\n"
        "| 1 | 直觉：标量/向量/矩阵/张量 | 3–4 |\n"
        "| 2 | 形式化定义 ($\\mathbb{R}^n$, $\\mathbb{R}^{m\\times n}$, 张量空间) | 4–5 |\n"
        "| 3 | NumPy 手写各算子 | 8–12 |\n"
        "| 4 | 可视化（向量、矩阵作用、特征值、PCA） | 3–5 |\n"
        "| 5 | 与花书对照 | 2–3 |\n"
        "| 6 | 综合练习 | 8–12 |\n"
        "| 7 | 自由探索 | 2–3 |\n"
        "| **8** | **AI 应用桥接（Workshop 弹药库）** | **6–8** |\n"
        "| CHECKPOINT | 自检清单 | — |\n"
    )


# ---------- Sec 0: Jupyter 入门 + 环境 ----------

def ch02_sec0(b: Builder):
    b.md(
        "---\n\n"
        "## Sec 0 — Jupyter 入门 + 环境\n\n"
        "你第一次用 Jupyter？这一节把「够用」的基础讲完。读完后你应该能：\n\n"
        "1. 认识 cell 和 kernel 两个核心概念\n"
        "2. 用快捷键熟练运行 / 新增 / 删除 cell\n"
        "3. 看懂 `In [n]` 编号、知道遇到 `NameError` 怎么办\n"
        "4. 重启 kernel 不慌\n\n"
        "**学法建议**：每读一段就**真的去试**——这一节的例题就是让你练肌肉记忆的。\n"
    )

    # 0.1
    b.md(
        "### 0.1 核心概念：notebook、cell、kernel\n\n"
        "- **Notebook**：你正在看的整个 `.ipynb` 文件，本质是一串 **cell** 的有序集合\n"
        "- **Cell**：notebook 的最小单元。两种：\n"
        "  - **Code cell**（灰底）：跑 Python 代码\n"
        "  - **Markdown cell**（白底，含格式）：写文字/标题/公式\n"
        "- **Kernel**：背后跑 Python 的进程。所有 code cell 共享同一个 kernel——**变量是跨 cell 持久的**，直到你重启 kernel\n\n"
        "**关键认知**：cell 的「显示顺序」≠「执行顺序」。看每个 code cell 左边的 `In [n]` 数字，n 是它**第几次被运行**。乱跳着跑 cell 是 bug 的常见根源。\n"
    )
    b.code(
        "# 这是一个 code cell。运行它（Shift+Enter）会看到下方输出 'hello'。\n"
        "print('hello, jupyter')"
    )
    b.md("上面运行后，cell 左边会出现 `In [1]`（如果是本次 kernel 启动后第一次跑）。再跑一次会变成 `In [2]`。试试。\n")

    # 0.2 shortcuts
    b.md(
        "### 0.2 关键快捷键\n\n"
        "Jupyter 有两个模式：\n"
        "- **编辑模式**（绿框）：在 cell 里输入文字\n"
        "- **命令模式**（蓝框）：操作 cell 本身（增删切换类型等）\n\n"
        "`Esc` 进命令模式，`Enter` 回编辑模式。\n\n"
        "**命令模式下最常用 6 个**：\n\n"
        "| 键 | 作用 |\n"
        "|---|------|\n"
        "| `Shift+Enter` | 运行当前 cell 并跳到下一个 |\n"
        "| `Ctrl+Enter` | 运行当前 cell，不跳 |\n"
        "| `A` / `B` | 在**上方** / **下方**插入新 cell |\n"
        "| `M` / `Y` | 把当前 cell 转为 **markdown** / **code** |\n"
        "| `DD`（连按两次 D）| 删除当前 cell |\n"
        "| `Z` | 撤销删除 |\n\n"
        "**编辑模式下最常用**：\n"
        "- `Tab`：补全 / 缩进\n"
        "- `Shift+Tab`：查看光标处函数的文档（再按一下展开）\n"
    )

    # 0.3 first hands-on exercise
    b.md(
        "### ✏️ 例题 0.E1：动手用快捷键\n\n"
        "1. 在**当前 markdown cell 下方**用 `B` 新建一个 code cell\n"
        "2. 输入 `2 + 3` 然后 `Shift+Enter` 运行\n"
        "3. 再按 `A` 在那个 code cell 上方插入新 cell；按 `M` 转为 markdown，输入 `# 我建的标题`，运行\n"
        "4. 选中刚建的 markdown cell，按 `DD` 删掉；按 `Z` 还原\n\n"
        "完成上面 4 步后，下面的题：把「动手」两个字加粗（Markdown 用 `**xxx**`）。提示：双击下面这个 cell 进编辑模式，改完 `Shift+Enter`。\n"
    )
    b.md("请改我：把 动手 加粗。\n")
    b.md(
        "> ✅ **检查**：上面那行如果出现 **动手** 两个加粗黑体字，就过了。"
        "（提示：把字串包在 `**` 里，比如 `**动手**`）\n"
    )

    # 0.4 markdown basics example with formula
    b.md(
        "### 0.3 Markdown 速查（够本章用）\n\n"
        "| 语法 | 效果 |\n|---|---|\n"
        "| `**粗体**` | **粗体** |\n"
        "| `*斜体*` | *斜体* |\n"
        "| `` `code` `` | `code` |\n"
        "| `# H1`、`## H2` | 标题 |\n"
        "| `- item` | 无序列表 |\n"
        "| 行内公式 `$x^2$` | $x^2$ |\n"
        "| 块公式 `$$ ... $$` | $$\\int_0^1 x\\, dx = \\tfrac12$$ |\n"
        "| `[文本](url)` | 链接 |\n"
    )

    # 0.5 NameError demo
    b.md(
        "### 0.4 常见坑 ①：忘了运行 import\n\n"
        "Kernel 全新启动时变量为空。**没运行 import 直接用 numpy 会 NameError**。下面这个 cell 故意演示——直接跑会报错：\n"
    )
    b.code(
        "# 故意：没 import numpy 就直接用——会 NameError\n"
        "# 取消下面这行的注释跑跑看，看完再把它注释回去\n"
        "# x = np.array([1, 2, 3])  # ← NameError: name 'np' is not defined\n"
        "pass"
    )
    b.md("解决方案就是**先跑** import cell。下一个 cell 就是 import：\n")
    b.code(
        "# 把所有 import 集中放在 notebook 顶部 cell（这是惯例）\n"
        "import sys\n"
        "sys.path.insert(0, '..')  # 让我们能 import 上一层的 utils\n\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "from utils import checks, viz\n\n"
        "print('imports ok')"
    )

    # 0.E2: trigger and fix NameError
    b.md(
        "### ✏️ 例题 0.E2：触发并修复 NameError\n\n"
        "1. 在下面的 code cell 里写 `y = mystery_var + 1` 然后运行——应该看到 `NameError: name 'mystery_var' is not defined`\n"
        "2. 在那一行**上方**插入新 cell（按 `A`），写 `mystery_var = 100`，运行\n"
        "3. 回到出错那 cell 重新运行——应该没问题，`y` 是 `101`\n"
        "4. 最后跑 `print(y)` 确认\n\n"
        "这个流程是修 `NameError` 的标准套路：**找到该被定义但还没运行的 cell，先跑它**。\n"
    )
    b.code(
        "# 你的练习区——按上面提示操作\n"
        "# 第一步：先跑这一行，看会报什么错\n"
        "# y = mystery_var + 1   # ← 取消注释让它跑\n"
        "pass",
        work_src=(
            "# 第一步：先跑这一行，看会报什么错\n"
            "# y = mystery_var + 1   # ← 取消注释让它跑\n"
            "pass"
        )
    )

    # 0.5 kernel restart
    b.md(
        "### 0.5 常见坑 ②：kernel 状态混乱 → Restart\n\n"
        "当你**乱序运行 cell**、覆盖了变量、或某段卡死，**最干净的修复**是：\n\n"
        "1. 顶部菜单 `Kernel → Restart Kernel`（快捷键 `0, 0`）\n"
        "2. 然后 `Kernel → Restart Kernel and Run All Cells` 全跑一遍\n\n"
        "重启 kernel 会**清空所有变量**——这是好事，能让你确认 notebook 真的能从头跑下来。\n"
    )
    b.md(
        "### ✏️ 例题 0.E3：观察 kernel 重启\n\n"
        "1. 在下方 code cell 写 `temp_var = 42` 然后运行\n"
        "2. 再来一个 cell `print(temp_var)`——应该输出 42\n"
        "3. 现在去菜单 `Kernel → Restart Kernel`\n"
        "4. **不重新运行第 1 步**，直接跑第 2 步——会 `NameError`，因为重启把 `temp_var` 清空了\n"
        "5. 修复：跑 `Kernel → Restart Kernel and Run All Cells`\n"
    )
    b.code("# 你的练习区\ntemp_var = 42\nprint(temp_var)")

    # 0.E4: hidden insight
    b.md(
        "### ✏️ 例题 0.E4：理解 In [n] 编号\n\n"
        "下面三个 code cell **乱序跑**：先跑第 3 个，再跑第 1 个，再跑第 2 个。\n"
        "观察每个 cell 左边的 `In [n]` 数字——**这个数字是执行序号，不是显示位置**。"
    )
    b.code("# Cell A — 我是第一个出现的 cell\nprint('A')")
    b.code("# Cell B — 我是第二个\nprint('B')")
    b.code("# Cell C — 我是第三个\nprint('C')")
    b.md(
        "如果你按 C → A → B 顺序跑，会看到 `In [1]` 在 C 这里、`In [2]` 在 A 这里、`In [3]` 在 B 这里。\n\n"
        "**这就是为什么 reproducible 的 notebook 必须能从头到尾按显示顺序一次跑通**——否则别人打开会得到不一样的结果。\n"
    )

    # 0.6 verify env
    b.md("### 0.6 验证环境（必跑）\n\n下面这行如果输出 numpy / matplotlib 版本，环境就 OK：\n")
    b.code(
        "import numpy, matplotlib, sys\n"
        "print('python    :', sys.version.split()[0])\n"
        "print('numpy     :', numpy.__version__)\n"
        "print('matplotlib:', matplotlib.__version__)"
    )


# ---------- Sec 1: 直觉先行 ----------

def ch02_sec1(b: Builder):
    b.md(
        "---\n\n## Sec 1 — 直觉先行：标量 / 向量 / 矩阵 / 张量\n\n"
        "**先抓直觉，再上数学**。这一节我们不写公式，只看「长什么样」。\n\n"
        "### 1.1 一个核心问题\n\n"
        "**用几个下标才能定位一个元素？**——这个数字就是数据对象的「阶」（rank / order）。\n"
    )
    b.md(
        "| 名称 | 几个下标 | 长什么样 | 日常例子 |\n"
        "|------|---------|---------|----------|\n"
        "| **标量** (scalar) | 0 | 一个数 | 此刻气温 `25` |\n"
        "| **向量** (vector) | 1 | 一行数 | 一天 24 小时气温 `[T_1, ..., T_24]` |\n"
        "| **矩阵** (matrix) | 2 | 一张表 | 一周×24 小时气温表 |\n"
        "| **张量** (tensor) | ≥ 3 | 多张表「摞」起来 | 10 城×7 天×24 小时气温 |\n"
    )
    b.md(
        "### 1.2 「摞」出来的张量\n\n"
        "想象一张二维表（矩阵）。把 10 张同样形状的表**摞成一摞**——就成了 3 阶张量。再把多摞同形状的「摞」摞成一组，就是 4 阶张量。\n\n"
        "深度学习里见到的最常见张量：\n\n"
        "- **彩色图片**：3 阶 `(H, W, 3)`——高、宽、RGB 三通道\n"
        "- **一批图片**：4 阶 `(N, H, W, 3)`——加一维 batch\n"
        "- **一批视频**：5 阶 `(N, T, H, W, 3)`——加一维时间\n"
    )

    # 例题 1.E1
    b.md(
        "### ✏️ 例题 1.E1：辨认阶数\n\n"
        "下面 4 个对象各是几阶？运行前**先猜**，再让代码验证：\n"
    )
    b.code(
        "a = 3.14\n"
        "b = [1, 2, 3, 4, 5]\n"
        "c = [[1, 2], [3, 4], [5, 6]]\n"
        "d = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]\n\n"
        "for name, x in [('a', a), ('b', b), ('c', c), ('d', d)]:\n"
        "    arr = np.array(x)\n"
        "    print(f'{name}: shape={arr.shape}, rank={arr.ndim}')\n"
    )
    b.md(
        "**预期**：`a` 是 0 阶（标量）、`b` 是 1 阶、`c` 是 2 阶、`d` 是 3 阶。"
        "数 `[[[ ... ]]]` 有几层 `[` 就是几阶。\n"
    )

    # 例题 1.E2
    b.md(
        "### ✏️ 例题 1.E2：shape 反推含义\n\n"
        "下面填空：给每个 shape 写一个**真实数据**的解释。\n"
    )
    b.code(
        "# 演示答案\n"
        "interpretations = {\n"
        "    (3,): '一个 3 维向量，比如 RGB 颜色 (r, g, b)',\n"
        "    (28, 28): '一张 28×28 灰度图（如 MNIST 一张数字）',\n"
        "    (28, 28, 3): '一张 28×28 彩色图（H×W×通道）',\n"
        "    (64, 28, 28, 3): '64 张 28×28 彩色图的 batch',\n"
        "    (10, 1, 32, 32, 3): '10 个视频，每个 1 帧 32×32 彩色',\n"
        "}\n"
        "for s, txt in interpretations.items():\n"
        "    print(f'shape={s}  →  {txt}')",
        work_src=(
            "# 填空：把 ___ 替换为你的解释（自然语言即可）\n"
            "interpretations = {\n"
            "    (3,): '___',\n"
            "    (28, 28): '___',\n"
            "    (28, 28, 3): '___',\n"
            "    (64, 28, 28, 3): '___',\n"
            "    (10, 1, 32, 32, 3): '___',\n"
            "}\n"
            "for s, txt in interpretations.items():\n"
            "    print(f'shape={s}  →  {txt}')"
        )
    )

    # 例题 1.E3
    b.md(
        "### ✏️ 例题 1.E3：阶 ≠ 形状的数字\n\n"
        "看到论文里写 $\\mathbf{T} \\in \\mathbb{R}^{4 \\times 4}$（典型例子：机器人学的 SE(3) 齐次变换矩阵）——它是几阶？"
        "运行前先猜。\n"
    )
    b.code(
        "T = np.eye(4)  # 4x4 单位矩阵\n"
        "print('shape:', T.shape)\n"
        "print('rank:', T.ndim)\n"
        "# 答案：2 阶（矩阵），不是 4 阶——4×4 是「形状的两个数」\n"
        "# 阶 = 形状元组的长度 = 2"
    )
    b.md(
        "**关键认知**：`np.ndim` 是「几阶」，`np.shape` 是「各维多大」。\n"
        "判断阶数**只数 shape 元组的长度**，跟里面具体数字无关。\n\n"
        "> 详见 vault notio [张量 → 常见误读](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E5%BC%A0%E9%87%8F)\n"
    )

    # 例题 1.E4
    b.md(
        "### ✏️ 例题 1.E4：图像展平为向量\n\n"
        "把一张 28×28 灰度图「展平」成长度 784 的向量——这是把矩阵看作「特殊的向量」。"
        "下面用 `np.random.randn` 假装一张图：\n"
    )
    b.code(
        "img = np.random.randn(28, 28)\n"
        "flat = img.flatten()  # 或 img.reshape(-1)\n"
        "checks.assert_shape('展平后', flat, (784,))\n"
        "print('原 shape:', img.shape, '→ 展平:', flat.shape)",
        work_src=(
            "img = np.random.randn(28, 28)\n"
            "# 提示：NumPy 数组有三个方法都能「展平成 1D」——\n"
            "#   .flatten()  /  .ravel()  /  .reshape(-1)\n"
            "# 任选一个，把 ___ 替换掉（注意有的需要参数，有的不需要）\n"
            "flat = img.___()\n"
            "checks.assert_shape('展平后', flat, (784,))\n"
            "print('原 shape:', img.shape, '→ 展平:', flat.shape)"
        )
    )


# ---------- Sec 2: 形式化定义 ----------

def ch02_sec2(b: Builder):
    _yuanwen(
        b,
        "标量, 向量, 矩阵, 张量",
        "**1. 标量 (Scalar)**：表示一个单独的**数**，通常用斜体小写字母表示，"
        "如 $s \\in \\mathbb{R},\\ n \\in \\mathbb{N}$。\n\n"
        "**2. 向量 (Vector)**：表示**一列数**，这些数有序排列的，可以通过下标获取对应值，"
        "通常用粗体小写字母表示：$\\boldsymbol{x} \\in \\mathbb{R}^n$，它表示元素取实数，"
        "且有 $n$ 个元素，第一个元素表示为：$x_1$。将向量写成列向量的形式：\n\n"
        "$$\\boldsymbol{x} = \\begin{bmatrix} x_1 \\\\ x_2 \\\\ \\cdots \\\\ x_n \\end{bmatrix}$$\n\n"
        "有时需要向量的子集，例如第 $1, 3, 6$ 个元素，那么我们可以令集合 $S = \\{1, 3, 6\\}$，"
        "然后用 $\\boldsymbol{x}_S$ 来表示这个子集。另外，我们用符号 $-$ 表示集合的补集："
        "$\\boldsymbol{x}_{-1}$ 表示除 $x_1$ 外 $\\boldsymbol{x}$ 中的所有元素，"
        "$\\boldsymbol{x}_{-S}$ 表示除 $x_1, x_3, x_6$ 外 $\\boldsymbol{x}$ 中的所有元素。\n\n"
        "**3. 矩阵 (Matrix)**：表示一个**二维数组**，每个元素的下标由两个数字确定，"
        "通常用大写粗体字母表示：$\\boldsymbol{A} \\in \\mathbb{R}^{m \\times n}$，"
        "它表示元素取实数的 $m$ 行 $n$ 列矩阵，其元素可以表示为：$A_{1,1}, A_{m,n}$。"
        "我们用「:」表示矩阵的一行或者一列：$\\boldsymbol{A}_{i,:}$ 为第 $i$ 行，"
        "$\\boldsymbol{A}_{:,j}$ 为第 $j$ 列。\n\n"
        "矩阵可以写成这样的形式：\n\n"
        "$$\\begin{bmatrix} A_{1,1} & A_{1,2} \\\\ A_{2,1} & A_{2,2} \\end{bmatrix}$$\n\n"
        "有时我们需要对矩阵进行**逐元素操作**，如将函数 $f$ 应用到 $\\boldsymbol{A}$ 的所有元素上，"
        "此时我们用 $f(\\boldsymbol{A})_{i,j}$ 表示。\n\n"
        "**4. 张量 (Tensor)**：**超过二维的数组**，我们用 $\\mathsf{A}$ 表示张量，"
        "$\\mathsf{A}_{i,j,k}$ 表示其元素（三维张量情况下）。",
        "# 花书原文配套代码：标量 / 向量 / 矩阵 / 张量\n"
        "import numpy as np\n\n"
        "s = 5\n"
        "v = np.array([1, 2])\n"
        "m = np.array([[1, 2], [3, 4]])\n"
        "t = np.array([\n"
        "    [[1, 2, 3], [4, 5, 6], [7, 8, 9]],\n"
        "    [[11, 12, 13], [14, 15, 16], [17, 18, 19]],\n"
        "    [[21, 22, 23], [24, 25, 26], [27, 28, 29]],\n"
        "])\n"
        "print('标量:', s)\n"
        "print('向量:', v)\n"
        "print('矩阵:\\n', m)\n"
        "print('张量:\\n', t)"
    )

    b.md(
        "---\n\n## Sec 2 — 形式化定义\n\n"
        "上面看完了原文的「四个对象」定义。这一节我们把它**更精确**地放在集合论的语言里——"
        "「住在哪个集合里」一句话说清。\n\n"
        "### 2.1 实数的 n 重笛卡尔乘积 $\\mathbb{R}^n$\n\n"
        "**笛卡尔乘积**：给两个集合 $A, B$，定义\n\n"
        "$$A \\times B = \\{(a, b) \\mid a \\in A,\\ b \\in B\\}$$\n\n"
        "即「所有有序对的集合」。把 $\\mathbb{R}$ 跟自己做 $n$ 次：\n\n"
        "$$\\mathbb{R}^n = \\underbrace{\\mathbb{R} \\times \\mathbb{R} \\times \\cdots \\times \\mathbb{R}}_{n\\text{ 次}}$$\n\n"
        "$\\mathbb{R}^n$ 的元素是 **$n$ 元组**（n-tuple）$(x_1, x_2, \\ldots, x_n)$，每个分量是实数。**这就是 n 维实向量**。\n"
    )
    b.md(
        "> ⚠️ 严格地说，$\\mathbb{R}^n$ 只是个**集合**（underlying set）。要让它成为「向量空间」，还要再附加加法和数乘运算——花书 p.28 没在这一步展开，但你心里要知道有这一层。详见 vault notio [张量](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E5%BC%A0%E9%87%8F)。\n"
    )
    b.md(
        "### 2.2 矩阵空间 $\\mathbb{R}^{m\\times n}$\n\n"
        "$m$ 行 $n$ 列的实矩阵全体。元素是 $\\mathbf{A}$，标量元素记作 $A_{i,j}$（$1 \\le i \\le m$，$1 \\le j \\le n$）。\n\n"
        "### 2.3 张量空间 $\\mathbb{R}^{n_1 \\times n_2 \\times \\cdots \\times n_k}$\n\n"
        "$k$ 阶实张量全体。元素 $\\mathsf{A}$ 用 $k$ 个下标索引：$\\mathsf{A}_{i_1, i_2, \\ldots, i_k}$。\n"
    )

    # 2.E1
    b.md(
        "### ✏️ 例题 2.E1：写出一个具体的 $\\mathbb{R}^3$ 元素\n\n"
        "构造一个 3 维向量 $\\mathbf{v}$，使得 $v_1 + v_2 + v_3 = 6$ 且 $v_1 = v_3$。"
    )
    b.code(
        "v = np.array([2.0, 2.0, 2.0])  # 一种解；其他如 [1, 4, 1]、[0, 6, 0] 也行\n"
        "checks.assert_true('和为 6', np.isclose(v.sum(), 6.0))\n"
        "checks.assert_true('v_1 == v_3', np.isclose(v[0], v[2]))\n"
        "print('v =', v)",
        work_src=(
            "v = np.array([___, ___, ___])  # 自己想一组满足条件的数\n"
            "checks.assert_true('和为 6', np.isclose(v.sum(), 6.0))\n"
            "checks.assert_true('v_1 == v_3', np.isclose(v[0], v[2]))\n"
            "print('v =', v)"
        )
    )

    # 2.E2
    b.md(
        "### ✏️ 例题 2.E2：shape 与阶的关系\n\n"
        "下表填空（先猜再运行）：\n"
    )
    b.code(
        "objects = [\n"
        "    ('标量',         np.array(3.14)),\n"
        "    ('R^5 向量',     np.zeros(5)),\n"
        "    ('R^(3x4) 矩阵', np.zeros((3, 4))),\n"
        "    ('R^(2x3x5)',    np.zeros((2, 3, 5))),\n"
        "    ('R^(N,H,W,C)',  np.zeros((10, 28, 28, 3))),\n"
        "]\n"
        "for name, x in objects:\n"
        "    print(f'{name:18s}  shape={str(x.shape):20s}  rank={x.ndim}')"
    )

    # 2.E3
    b.md(
        "### ✏️ 例题 2.E3：构造一个 3 阶张量\n\n"
        "用 NumPy 构造形状为 `(2, 3, 4)` 的张量，每个元素是它三个下标的和："
        "$\\mathsf{A}_{i,j,k} = i + j + k$（下标从 0 开始）。\n"
    )
    b.code(
        "A = np.zeros((2, 3, 4))\n"
        "for i in range(2):\n"
        "    for j in range(3):\n"
        "        for k in range(4):\n"
        "            A[i, j, k] = i + j + k\n"
        "# 或更 numpy 的写法：\n"
        "# i, j, k = np.indices((2, 3, 4))\n"
        "# A = i + j + k\n"
        "checks.assert_equal('A[1,2,3]', A[1, 2, 3], 6)\n"
        "checks.assert_equal('A[0,0,0]', A[0, 0, 0], 0)\n"
        "print(A)",
        work_src=(
            "A = np.zeros((2, 3, 4))\n"
            "for i in range(___):\n"
            "    for j in range(___):\n"
            "        for k in range(___):\n"
            "            A[i, j, k] = ___\n"
            "checks.assert_equal('A[1,2,3]', A[1, 2, 3], 6)\n"
            "checks.assert_equal('A[0,0,0]', A[0, 0, 0], 0)\n"
            "print(A)"
        )
    )

    # 2.E4
    b.md(
        "### ✏️ 例题 2.E4：image batch 形状解读\n\n"
        "你拿到一批形状 `(32, 224, 224, 3)` 的数据。填空回答下面 4 个问题：\n"
    )
    b.code(
        "shape = (32, 224, 224, 3)\n"
        "answers = {\n"
        "    '阶数 (rank)': 4,\n"
        "    '一共多少张图': 32,\n"
        "    '每张图像素数 (H*W)': 224 * 224,\n"
        "    '每个像素几个通道': 3,\n"
        "}\n"
        "for k, v in answers.items():\n"
        "    print(f'  {k:25s} = {v}')",
        work_src=(
            "shape = (32, 224, 224, 3)\n"
            "answers = {\n"
            "    '阶数 (rank)': ___,\n"
            "    '一共多少张图': ___,\n"
            "    '每张图像素数 (H*W)': ___,\n"
            "    '每个像素几个通道': ___,\n"
            "}\n"
            "for k, v in answers.items():\n"
            "    print(f'  {k:25s} = {v}')"
        )
    )


# ---------- Sec 3: NumPy 手写各算子 ----------

def ch02_sec3(b: Builder):
    b.md(
        "---\n\n## Sec 3 — NumPy 手写各算子\n\n"
        "这一节是**这章的核心**。每个算子三步走：\n\n"
        "1. **数学定义**——公式说清\n"
        "2. **手写实现**——纯 Python `for` 循环，目的是看清楚机制\n"
        "3. **NumPy 一行**——和官方实现对照验证\n"
    )

    # 3.1 array creation
    b.md(
        "### 3.1 创建数组——基本工具\n\n"
        "NumPy 创建数组的 4 个常用函数：\n"
    )
    b.code(
        "print('zeros:', np.zeros((2, 3)), sep='\\n')\n"
        "print('ones:',  np.ones((2, 3)),  sep='\\n')\n"
        "print('eye(3):', np.eye(3), sep='\\n')\n"
        "print('arange:', np.arange(0, 10, 2))\n"
        "print('随机:', np.random.randn(3, 3), sep='\\n')"
    )

    # 3.E1
    b.md(
        "### ✏️ 例题 3.E1：构造特定矩阵\n\n"
        "构造 $\\mathbf{M} \\in \\mathbb{R}^{4 \\times 4}$ 满足：对角线全 5，其余位置全 -1。"
    )
    b.code(
        "M = 5 * np.eye(4) + (-1) * (np.ones((4, 4)) - np.eye(4))\n"
        "# 等价的另一写法：\n"
        "# M = -np.ones((4, 4)); np.fill_diagonal(M, 5)\n"
        "expected = np.array([\n"
        "    [5, -1, -1, -1],\n"
        "    [-1, 5, -1, -1],\n"
        "    [-1, -1, 5, -1],\n"
        "    [-1, -1, -1, 5],\n"
        "])\n"
        "checks.assert_equal('M', M, expected)\n"
        "print(M)",
        work_src=(
            "M = ___  # 用 np.eye 和 np.ones 组合\n"
            "expected = np.array([\n"
            "    [5, -1, -1, -1],\n"
            "    [-1, 5, -1, -1],\n"
            "    [-1, -1, 5, -1],\n"
            "    [-1, -1, -1, 5],\n"
            "])\n"
            "checks.assert_equal('M', M, expected)\n"
            "print(M)"
        )
    )

    # 3.2 transpose
    _yuanwen(
        b,
        "矩阵转置",
        "矩阵转置 (Transpose) 相当于**沿着对角线翻转**，定义如下：\n\n"
        "$$A^\\top_{i,j} = A_{j,i}$$\n\n"
        "矩阵转置的转置等于矩阵本身：\n\n"
        "$$(A^\\top)^\\top = A$$\n\n"
        "转置将矩阵的形状从 $m \\times n$ 变成了 $n \\times m$。\n\n"
        "**向量**可以看成是**只有一列的矩阵**，为了方便，我们可以使用行向量加转置的操作，"
        "如：$\\boldsymbol{x} = [x_1, x_2, x_3]^\\top$。\n\n"
        "**标量**也可以看成是**一行一列的矩阵**，其转置等于它自身：$a^\\top = a$。",
        "# 花书原文配套代码：转置\n"
        "A = np.array([[1.0, 2.0], [1.0, 0.0], [2.0, 3.0]])\n"
        "A_t = A.transpose()\n"
        "print('A:\\n', A)\n"
        "print('A 的转置:\\n', A_t)"
    )

    b.md(        "### 3.2 转置 (transpose)\n\n"
        "$$\\left(\\mathbf{A}^\\top\\right)_{i,j} = A_{j,i}$$\n\n"
        "几何上：以主对角线为轴的镜像。\n"
    )
    b.code(
        "def my_transpose(A):\n"
        "    m, n = A.shape\n"
        "    AT = np.zeros((n, m))\n"
        "    for i in range(m):\n"
        "        for j in range(n):\n"
        "            AT[j, i] = A[i, j]\n"
        "    return AT\n\n"
        "A = np.array([[1, 2, 3], [4, 5, 6]])\n"
        "print('A:', A, sep='\\n')\n"
        "print('A^T (手写):', my_transpose(A), sep='\\n')\n"
        "print('A^T (numpy):', A.T, sep='\\n')\n"
        "checks.assert_equal('转置一致', my_transpose(A), A.T)"
    )

    # 3.E2
    b.md("### ✏️ 例题 3.E2：转置的转置\n\n证明 $(\\mathbf{A}^\\top)^\\top = \\mathbf{A}$ 在 NumPy 中成立。")
    b.code(
        "A = np.random.randn(3, 5)\n"
        "checks.assert_equal('(A.T).T == A', A.T.T, A)",
        work_src=(
            "A = np.random.randn(3, 5)\n"
            "# 填空：用 A 写出双重转置后比较\n"
            "checks.assert_equal('(A.T).T == A', ___, A)"
        )
    )

    # 3.2.5 矩阵加法 + 数乘 + 广播
    _yuanwen(
        b,
        "矩阵加法",
        "**加法**即对应元素相加，要求两个矩阵的形状一样：\n\n"
        "$$C = A + B,\\quad C_{i,j} = A_{i,j} + B_{i,j}$$\n\n"
        "**数乘**即一个标量与矩阵每个元素相乘：\n\n"
        "$$D = a \\cdot B + c,\\quad D_{i,j} = a \\cdot B_{i,j} + c$$\n\n"
        "有时我们允许矩阵和向量相加的，得到一个矩阵，把 $\\boldsymbol{b}$ 加到了 $\\boldsymbol{A}$ 的每一行上，"
        "本质上是构造了一个将 $\\boldsymbol{b}$ 按行复制的一个新矩阵，这种机制叫做**广播 (Broadcasting)**：\n\n"
        "$$C = A + \\boldsymbol{b},\\quad C_{i,j} = A_{i,j} + b_j$$",
        "# 花书原文配套代码：加法 + 广播\n"
        "a = np.array([[1.0, 2.0], [3.0, 4.0]])\n"
        "b_mat = np.array([[6.0, 7.0], [8.0, 9.0]])\n"
        "print('矩阵相加:\\n', a + b_mat)"
    )

    b.md(        "### 3.2.5 矩阵加法、数乘、广播\n\n"
        "**矩阵加法**（element-wise）：形状相同的两矩阵对应位置相加：\n\n"
        "$$C_{i,j} = A_{i,j} + B_{i,j}$$\n\n"
        "**数乘**：标量乘矩阵 = 每元素分别乘：\n\n"
        "$$(\\alpha \\mathbf{A})_{i,j} = \\alpha \\cdot A_{i,j}$$\n\n"
        "NumPy 用 `+ - * /` 直接做（⚠️ `*` 是 Hadamard 不是矩阵乘——下一节讲 Hadamard）。\n"
    )
    b.code(
        "A = np.array([[1, 2], [3, 4]])\n"
        "B = np.array([[10, 20], [30, 40]])\n"
        "print('A + B:', A + B, sep='\\n')\n"
        "print('A - B:', A - B, sep='\\n')\n"
        "print('2 * A:', 2 * A, sep='\\n')\n"
        "print('A + 100:', A + 100, sep='\\n')"
    )

    b.md(
        "#### 广播（broadcasting）\n\n"
        "形状**不完全相同**的数组也能逐元素运算——NumPy 自动「扩展」成兼容形状。"
        "深度学习里**极常用**：一个向量加到矩阵的每一行（例如给每个样本加同一个 bias）。\n\n"
        "广播规则（简化版）：从尾部对齐，每一维要么相等、要么有一个是 1，"
        "维度数不够的自动当作 1。"
    )
    b.code(
        "A = np.array([[1, 2, 3], [4, 5, 6]])  # shape (2, 3)\n"
        "row = np.array([10, 20, 30])          # shape (3,)\n"
        "# A + row：自动把 row 加到 A 的每一行\n"
        "print('A + row:', A + row, sep='\\n')\n\n"
        "# 列方向：用 col[:, None] 让 col 变成 (2, 1)\n"
        "col = np.array([100, 200])             # shape (2,)\n"
        "print('A + col[:, None]:', A + col[:, None], sep='\\n')"
    )

    # 3.E_add
    b.md("### ✏️ 例题 3.E_add：手写矩阵加法（双 for 循环）")
    b.code(
        "def my_add(A, B):\n"
        "    assert A.shape == B.shape\n"
        "    m, n = A.shape\n"
        "    C = np.zeros((m, n))\n"
        "    for i in range(m):\n"
        "        for j in range(n):\n"
        "            C[i, j] = A[i, j] + B[i, j]\n"
        "    return C\n\n"
        "A = np.array([[1, 2], [3, 4]])\n"
        "B = np.array([[5, 6], [7, 8]])\n"
        "checks.assert_equal('手写加法', my_add(A, B), A + B)",
        work_src=(
            "def my_add(A, B):\n"
            "    assert A.shape == B.shape\n"
            "    m, n = A.shape\n"
            "    C = np.zeros((m, n))\n"
            "    # 提示：跟 my_hadamard 一样的双 for 结构（你后面会写到），把乘改成加\n"
            "    for i in range(___):\n"
            "        for j in range(___):\n"
            "            C[i, j] = ___\n"
            "    return C\n\n"
            "A = np.array([[1, 2], [3, 4]])\n"
            "B = np.array([[5, 6], [7, 8]])\n"
            "checks.assert_equal('手写加法', my_add(A, B), A + B)"
        )
    )

    # 3.E_bcast
    b.md(
        "### ✏️ 例题 3.E_bcast：预测广播形状\n\n"
        "下面 4 个表达式，运行**前**先猜——哪些能跑？跑得通的结果形状是？"
    )
    b.code(
        "A = np.zeros((3, 4))\n"
        "v = np.zeros(4)\n"
        "u = np.zeros(3)\n"
        "s = 5\n\n"
        "# 1. A + v: v 长度 4 = A 最后一维 → 广播到每一行，结果 (3, 4)\n"
        "print('A + v shape:', (A + v).shape)\n\n"
        "# 2. A + s: 标量广播到每元素，结果 (3, 4)\n"
        "print('A + s shape:', (A + s).shape)\n\n"
        "# 3. A + u: u 长度 3 ≠ A 最后一维 4 → 报错\n"
        "try:\n"
        "    _ = A + u\n"
        "except ValueError as e:\n"
        "    print('A + u 失败:', e)\n\n"
        "# 4. A + u[:, None]: u[:, None] shape (3, 1) → 广播到每一列，结果 (3, 4)\n"
        "print('A + u[:, None] shape:', (A + u[:, None]).shape)"
    )

    # 3.3 Hadamard
    b.md(
        "### 3.3 Hadamard 乘积（逐元素乘）⊙\n\n"
        "$$(\\mathbf{A} \\odot \\mathbf{B})_{i,j} = A_{i,j} \\cdot B_{i,j}$$\n\n"
        "**要求 A、B 形状完全相同**。NumPy 里的 `*` 就是 Hadamard，不是矩阵乘！\n\n"
        "> 详见 vault notio [Hadamard 乘积](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2FHadamard%20%E4%B9%98%E7%A7%AF)\n"
    )
    b.code(
        "A = np.array([[1, 2], [3, 4]])\n"
        "B = np.array([[5, 6], [7, 8]])\n"
        "had = A * B  # Hadamard\n"
        "print('Hadamard A⊙B:', had, sep='\\n')\n"
        "checks.assert_equal('Hadamard', had, np.array([[5, 12], [21, 32]]))"
    )

    # 3.E3
    b.md(
        "### ✏️ 例题 3.E3：手写 Hadamard\n\n"
        "用 for 循环实现 Hadamard，不要用 `*` 或 `np.multiply`。"
    )
    b.code(
        "def my_hadamard(A, B):\n"
        "    assert A.shape == B.shape\n"
        "    m, n = A.shape\n"
        "    C = np.zeros((m, n))\n"
        "    for i in range(m):\n"
        "        for j in range(n):\n"
        "            C[i, j] = A[i, j] * B[i, j]\n"
        "    return C\n\n"
        "A = np.array([[1, 2], [3, 4]])\n"
        "B = np.array([[5, 6], [7, 8]])\n"
        "checks.assert_equal('手写 Hadamard 对', my_hadamard(A, B), A * B)",
        work_src=(
            "def my_hadamard(A, B):\n"
            "    assert A.shape == B.shape\n"
            "    m, n = A.shape\n"
            "    C = np.zeros((m, n))\n"
            "    for i in range(___):\n"
            "        for j in range(___):\n"
            "            C[i, j] = ___\n"
            "    return C\n\n"
            "A = np.array([[1, 2], [3, 4]])\n"
            "B = np.array([[5, 6], [7, 8]])\n"
            "checks.assert_equal('手写 Hadamard 对', my_hadamard(A, B), A * B)"
        )
    )

    # 3.4 matmul
    _yuanwen(
        b,
        "矩阵乘法",
        "两个矩阵相乘得到第三个矩阵，我们需要 $A$ 的形状为 $m \\times n$，$B$ 的形状为 $n \\times p$，"
        "得到的矩阵为 $C$ 的形状为 $m \\times p$：\n\n"
        "$$C = AB$$\n\n"
        "具体定义为：\n\n"
        "$$C_{i,j} = \\sum_k A_{i,k} B_{k,j}$$\n\n"
        "注意**矩阵乘法不是元素对应相乘**，元素对应相乘又叫 Hadamard 乘积，记作 $A \\odot B$。\n\n"
        "向量可以看作是列为 1 的矩阵，两个相同维数的向量 $\\boldsymbol{x}$ 和 $\\boldsymbol{y}$ 的点乘 (Dot Product) 或者内积，"
        "可以表示为 $\\boldsymbol{x}^\\top \\boldsymbol{y}$。\n\n"
        "我们也可以把矩阵乘法理解为：$C_{i,j}$ 表示 $A$ 的第 $i$ 行与 $B$ 的第 $j$ 列的点积。",
        "# 花书原文配套代码：矩阵乘 vs Hadamard vs 点积\n"
        "m1 = np.array([[1.0, 3.0], [1.0, 0.0]])\n"
        "m2 = np.array([[1.0, 2.0], [5.0, 0.0]])\n"
        "print('按矩阵乘法规则:\\n', np.dot(m1, m2))\n"
        "print('按逐元素相乘:\\n', np.multiply(m1, m2))\n"
        "print('按逐元素相乘:\\n', m1 * m2)\n\n"
        "v1 = np.array([1.0, 2.0])\n"
        "v2 = np.array([4.0, 5.0])\n"
        "print('向量内积:', np.dot(v1, v2))"
    )

    b.md(        "### 3.4 矩阵乘法 @\n\n"
        "$$C_{i,j} = \\sum_{k=1}^{n} A_{i,k}\\, B_{k,j}$$\n\n"
        "**A 列数 = B 行数**（设为 $n$）。结果 C 形状 $m \\times p$。\n\n"
        "**直觉**：C 的第 $(i,j)$ 格 = A 的第 $i$ 行 与 B 的第 $j$ 列 的点积。\n\n"
        "> 详见 vault notio [矩阵乘法](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E7%9F%A9%E9%98%B5%E4%B9%98%E6%B3%95)\n"
    )
    b.code(
        "def my_matmul(A, B):\n"
        "    m, n = A.shape\n"
        "    n2, p = B.shape\n"
        "    assert n == n2, f'A 列 {n} ≠ B 行 {n2}'\n"
        "    C = np.zeros((m, p))\n"
        "    for i in range(m):\n"
        "        for j in range(p):\n"
        "            for k in range(n):\n"
        "                C[i, j] += A[i, k] * B[k, j]\n"
        "    return C\n\n"
        "A = np.array([[1, 2, 3], [4, 5, 6]])           # 2x3\n"
        "B = np.array([[7, 8], [9, 10], [11, 12]])      # 3x2\n"
        "print('手写:', my_matmul(A, B), sep='\\n')\n"
        "print('A @ B:', A @ B, sep='\\n')\n"
        "checks.assert_equal('矩阵乘一致', my_matmul(A, B), A @ B)"
    )

    # 3.E4
    b.md(
        "### ✏️ 例题 3.E4：预测题——shape 推理\n\n"
        "运行**前**先猜：下面 `A @ B` 的 shape 是多少？`A * B` 能跑吗？\n"
    )
    b.code(
        "A = np.random.randn(3, 4)\n"
        "B = np.random.randn(4, 5)\n"
        "print('A.shape:', A.shape, ' B.shape:', B.shape)\n"
        "print('A @ B shape:', (A @ B).shape)  # 预测：(3, 5)\n"
        "try:\n"
        "    C = A * B  # 预测：报错（shape 不匹配）\n"
        "    print('A * B:', C.shape)\n"
        "except ValueError as e:\n"
        "    print('A * B 失败：', e)"
    )

    # 3.E5
    b.md(
        "### ✏️ 例题 3.E5：矩阵乘不交换\n\n"
        "造两个**形状兼容相互乘**的方阵 $\\mathbf{A}, \\mathbf{B}$，验证 $\\mathbf{AB} \\ne \\mathbf{BA}$。"
    )
    b.code(
        "A = np.array([[1, 2], [3, 4]])\n"
        "B = np.array([[5, 6], [7, 8]])\n"
        "AB = A @ B\n"
        "BA = B @ A\n"
        "print('AB:', AB, sep='\\n')\n"
        "print('BA:', BA, sep='\\n')\n"
        "checks.assert_true('AB != BA', not np.allclose(AB, BA))",
        work_src=(
            "A = np.array([[1, 2], [3, 4]])\n"
            "B = np.array([[5, 6], [7, 8]])\n"
            "AB = ___\n"
            "BA = ___\n"
            "print('AB:', AB, sep='\\n')\n"
            "print('BA:', BA, sep='\\n')\n"
            "checks.assert_true('AB != BA', not np.allclose(AB, BA))"
        )
    )

    # 3.4.5 单位矩阵 + 矩阵的逆 + 解线性方程组
    _yuanwen(
        b,
        "单位矩阵",
        "为了引入矩阵的逆，我们需要先定义**单位矩阵 (Identity Matrix)**："
        "单位矩阵乘以任意一个向量等于这个向量本身。记 $\\boldsymbol{I}_n$ 为保持 $n$ 维向量不变的单位矩阵，即：\n\n"
        "$$\\boldsymbol{I}_n \\in \\mathbb{R}^{n \\times n},\\ \\forall \\boldsymbol{x} \\in \\mathbb{R}^n,\\ \\boldsymbol{I}_n \\boldsymbol{x} = \\boldsymbol{x}$$\n\n"
        "单位矩阵的结构十分简单，所有的对角元素都为 1，其他元素都为 0，如：\n\n"
        "$$\\boldsymbol{I}_3 = \\begin{bmatrix} 1 & 0 & 0 \\\\ 0 & 1 & 0 \\\\ 0 & 0 & 1 \\end{bmatrix}$$",
        "# 花书原文配套代码：单位矩阵\n"
        "print(np.identity(3))"
    )

    b.md(        "### 3.4.5 单位矩阵（Identity）\n\n"
        "**单位矩阵** $\\mathbf{I}_n \\in \\mathbb{R}^{n \\times n}$：对角线全 1、其余全 0。\n\n"
        "$$\\mathbf{I}_3 = \\begin{bmatrix} 1 & 0 & 0 \\\\ 0 & 1 & 0 \\\\ 0 & 0 & 1 \\end{bmatrix}$$\n\n"
        "**核心性质**：对任意形状兼容的矩阵 $\\mathbf{A}$，\n\n"
        "$$\\mathbf{I}\\mathbf{A} = \\mathbf{A}\\mathbf{I} = \\mathbf{A}$$\n\n"
        "可以把它理解为「矩阵乘法里的 1」。NumPy 直接用 `np.eye(n)` 造。\n"
    )
    b.code(
        "I3 = np.eye(3)\n"
        "print('I_3:', I3, sep='\\n')\n\n"
        "A = np.array([[1., 2., 3.], [4., 5., 6.]])  # 2x3\n"
        "print('I_2 @ A == A?', np.allclose(np.eye(2) @ A, A))\n"
        "print('A @ I_3 == A?', np.allclose(A @ np.eye(3), A))"
    )

    _yuanwen(
        b,
        "矩阵的逆",
        "矩阵 $\\boldsymbol{A}$ 的**逆 (Inversion)** 记作 $\\boldsymbol{A}^{-1}$，定义为一个矩阵使得：\n\n"
        "$$\\boldsymbol{A}^{-1} \\boldsymbol{A} = \\boldsymbol{I}_n$$\n\n"
        "如果 $\\boldsymbol{A}^{-1}$ 存在，那么线性方程组 $\\boldsymbol{A}\\boldsymbol{x} = \\boldsymbol{b}$ 的解为：\n\n"
        "$$\\boldsymbol{A}^{-1} \\boldsymbol{A} \\boldsymbol{x} = \\boldsymbol{I}_n \\boldsymbol{x} = \\boldsymbol{x} = \\boldsymbol{A}^{-1} \\boldsymbol{b}$$",
        "# 花书原文配套代码：矩阵的逆\n"
        "A = np.array([[1.0, 2.0], [3.0, 4.0]])\n"
        "A_inv = np.linalg.inv(A)\n"
        "print('A 的逆矩阵:\\n', A_inv)"
    )

    b.md(        "### 3.4.6 矩阵的逆（Inverse）\n\n"
        "对**方阵** $\\mathbf{A} \\in \\mathbb{R}^{n \\times n}$，若存在矩阵 $\\mathbf{A}^{-1}$ 使得\n\n"
        "$$\\mathbf{A}\\mathbf{A}^{-1} = \\mathbf{A}^{-1}\\mathbf{A} = \\mathbf{I}_n$$\n\n"
        "则 $\\mathbf{A}^{-1}$ 是 $\\mathbf{A}$ 的**逆矩阵**，$\\mathbf{A}$ 称为**可逆**（invertible / non-singular）。\n\n"
        "**不是所有方阵都可逆**：行列式（determinant）为 0 的矩阵叫**奇异矩阵**（singular），无逆。"
        "几何上：A 把高维空间「压扁」成低维，信息丢了，没法回去。\n\n"
        "NumPy: `np.linalg.inv(A)`。\n"
    )
    b.code(
        "A = np.array([[4., 7.], [2., 6.]])\n"
        "A_inv = np.linalg.inv(A)\n"
        "print('A_inv:', A_inv, sep='\\n')\n\n"
        "# 验证 A @ A_inv == I\n"
        "I = A @ A_inv\n"
        "print('A @ A_inv:', I, sep='\\n')\n"
        "print('近似 I_2?', np.allclose(I, np.eye(2)))"
    )

    b.md(
        "### 3.4.7 用矩阵的逆解线性方程组\n\n"
        "经典问题：给 $\\mathbf{A}\\mathbf{x} = \\mathbf{b}$，求 $\\mathbf{x}$。\n\n"
        "**理论**：左乘 $\\mathbf{A}^{-1}$，得 $\\mathbf{x} = \\mathbf{A}^{-1}\\mathbf{b}$。\n\n"
        "**实际**：用 `np.linalg.solve(A, b)`——内部用 LU 分解，比「先求逆再相乘」**更稳定、更快**。"
        "实际工程中**几乎从不**手动算逆来解方程。\n"
    )
    b.code(
        "# 解方程组：2x + 3y = 8,  x − y = −1\n"
        "A = np.array([[2., 3.], [1., -1.]])\n"
        "b = np.array([8., -1.])\n\n"
        "# 方法 A：用逆\n"
        "x_inv = np.linalg.inv(A) @ b\n"
        "# 方法 B：solve（推荐）\n"
        "x_solve = np.linalg.solve(A, b)\n\n"
        "print('via inv  :', x_inv)\n"
        "print('via solve:', x_solve)\n"
        "# 期望 x=1, y=2"
    )

    # 3.E_solve
    b.md("### ✏️ 例题 3.E_solve：解 2x2 方程组")
    b.code(
        "# 解 3x + y = 9,  x + 2y = 8\n"
        "A = np.array([[3., 1.], [1., 2.]])\n"
        "b = np.array([9., 8.])\n"
        "x = np.linalg.solve(A, b)\n"
        "checks.assert_close('解', x, np.array([2., 3.]))  # 验：3·2+3=9, 2+2·3=8\n"
        "print('x =', x)",
        work_src=(
            "# 解 3x + y = 9,  x + 2y = 8\n"
            "A = np.array([[3., 1.], [1., 2.]])\n"
            "b = np.array([9., 8.])\n"
            "# 提示：用 np.linalg.solve(A, b)（比 inv 更好）\n"
            "x = ___\n"
            "checks.assert_close('解', x, np.array([2., 3.]))\n"
            "print('x =', x)"
        )
    )

    # 3.E_sing
    b.md(
        "### ✏️ 例题 3.E_sing：奇异矩阵无逆\n\n"
        "构造一个奇异矩阵（两行成比例），观察 `np.linalg.inv` 的行为。"
    )
    b.code(
        "A_sing = np.array([[1., 2.], [2., 4.]])  # 第二行 = 2 × 第一行\n"
        "det = np.linalg.det(A_sing)\n"
        "print('行列式:', det)  # 数值上应非常接近 0\n\n"
        "try:\n"
        "    A_inv = np.linalg.inv(A_sing)\n"
        "    print('竟然算出来了（但值是天文数字）:', A_inv)\n"
        "except np.linalg.LinAlgError as e:\n"
        "    print('不可逆:', e)"
    )

    b.md(
        "### 矩阵逆的性质\n\n"
        "- $(\\mathbf{A}^{-1})^{-1} = \\mathbf{A}$\n"
        "- $(\\mathbf{A}\\mathbf{B})^{-1} = \\mathbf{B}^{-1}\\mathbf{A}^{-1}$（**顺序反转**，跟转置 $(\\mathbf{AB})^\\top = \\mathbf{B}^\\top \\mathbf{A}^\\top$ 完全类似）\n"
        "- $(\\mathbf{A}^\\top)^{-1} = (\\mathbf{A}^{-1})^\\top$（逆与转置可换序）\n"
    )
    # 3.E_inv_AB
    b.md("### ✏️ 例题 3.E_inv_AB：验证 $(\\mathbf{AB})^{-1} = \\mathbf{B}^{-1}\\mathbf{A}^{-1}$")
    b.code(
        "np.random.seed(0)\n"
        "A = np.random.randn(3, 3)\n"
        "B = np.random.randn(3, 3)\n"
        "lhs = np.linalg.inv(A @ B)\n"
        "rhs = np.linalg.inv(B) @ np.linalg.inv(A)\n"
        "checks.assert_close('(AB)^-1 == B^-1 A^-1', lhs, rhs)",
        work_src=(
            "np.random.seed(0)\n"
            "A = np.random.randn(3, 3)\n"
            "B = np.random.randn(3, 3)\n"
            "lhs = np.linalg.inv(___)     # 左边：(AB)^-1\n"
            "rhs = np.linalg.inv(B) @ np.linalg.inv(___)  # 右边：B^-1 A^-1\n"
            "checks.assert_close('(AB)^-1 == B^-1 A^-1', lhs, rhs)"
        )
    )

    # 3.5 inner product
    b.md(
        "### 3.5 点积 (dot / inner product)\n\n"
        "$$\\mathbf{a} \\cdot \\mathbf{b} = \\sum_{i=1}^{n} a_i b_i$$\n\n"
        "标量结果。NumPy：`np.dot(a, b)` 或 `a @ b`（1D 时矩阵乘退化为点积）。\n"
    )
    b.code(
        "a = np.array([1, 2, 3])\n"
        "b = np.array([4, 5, 6])\n"
        "print('np.dot:', np.dot(a, b))   # 1*4 + 2*5 + 3*6 = 32\n"
        "print('a @ b :', a @ b)\n"
        "print('手写  :', sum(a[i] * b[i] for i in range(len(a))))"
    )

    # 3.E6
    b.md("### ✏️ 例题 3.E6：手写点积")
    b.code(
        "def my_dot(a, b):\n"
        "    assert len(a) == len(b)\n"
        "    s = 0.0\n"
        "    for i in range(len(a)):\n"
        "        s += a[i] * b[i]\n"
        "    return s\n\n"
        "checks.assert_close('点积', my_dot(np.array([1, 2, 3]), np.array([4, 5, 6])), 32)",
        work_src=(
            "def my_dot(a, b):\n"
            "    assert len(a) == len(b)\n"
            "    s = 0.0\n"
            "    for i in range(len(a)):\n"
            "        s += ___\n"
            "    return s\n\n"
            "checks.assert_close('点积', my_dot(np.array([1, 2, 3]), np.array([4, 5, 6])), 32)"
        )
    )

    # 3.6 trace
    b.md(
        "### 3.6 矩阵迹 (trace)\n\n"
        "$$\\mathrm{tr}(\\mathbf{A}) = \\sum_{i} A_{i,i}$$\n\n"
        "对角线之和。性质：$\\mathrm{tr}(\\mathbf{AB}) = \\mathrm{tr}(\\mathbf{BA})$（即便 $\\mathbf{AB} \\ne \\mathbf{BA}$）。\n"
    )
    b.code(
        "A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])\n"
        "print('对角线:', np.diag(A))\n"
        "print('trace :', np.trace(A))  # 1+5+9 = 15\n"
        "print('手写  :', sum(A[i, i] for i in range(A.shape[0])))"
    )

    # 3.E7
    b.md("### ✏️ 例题 3.E7：验证 tr(AB) = tr(BA)")
    b.code(
        "A = np.random.randn(4, 3)\n"
        "B = np.random.randn(3, 4)\n"
        "tr_AB = np.trace(A @ B)\n"
        "tr_BA = np.trace(B @ A)\n"
        "checks.assert_close('tr(AB) == tr(BA)', tr_AB, tr_BA)\n"
        "print(f'tr(AB)={tr_AB:.6f}  tr(BA)={tr_BA:.6f}')",
        work_src=(
            "A = np.random.randn(4, 3)\n"
            "B = np.random.randn(3, 4)\n"
            "tr_AB = np.trace(___)\n"
            "tr_BA = np.trace(___)\n"
            "checks.assert_close('tr(AB) == tr(BA)', tr_AB, tr_BA)\n"
            "print(f'tr(AB)={tr_AB:.6f}  tr(BA)={tr_BA:.6f}')"
        )
    )

    # 3.7 norms
    _yuanwen(
        b,
        "范数",
        "通常我们用**范数 (norm)** 来衡量向量，向量的 $L^p$ 范数定义为：\n\n"
        "$$\\|\\boldsymbol{x}\\|_p = \\left(\\sum_i |x_i|^p\\right)^{1/p},\\ p \\in \\mathbb{R},\\ p \\geq 1$$\n\n"
        "$L^2$ 范数，也称**欧几里得范数 (Euclidean norm)**，是**向量 $\\boldsymbol{x}$ 到原点的欧几里得距离**。"
        "有时也用 $L^2$ 范数的平方来衡量向量：$\\boldsymbol{x}^\\top \\boldsymbol{x}$。"
        "事实上，平方 $L^2$ 范数在计算上更为便利，"
        "例如它的对 $\\boldsymbol{x}$ 梯度的各个分量只依赖于 $\\boldsymbol{x}$ 的对应的各个分量，"
        "而 $L^2$ 范数对 $\\boldsymbol{x}$ 梯度的各个分量要依赖于整个 $\\boldsymbol{x}$ 向量。\n\n"
        "$L^1$ 范数：$L^2$ 范数并不一定适用于所有的情况，它在原点附近的增长就十分缓慢，"
        "因此不适用于需要区别 0 和非常小但是非 0 值的情况。$L^1$ 范数就是一个比较好的选择，"
        "它在所有方向上的增长速率都是一样的，定义为：\n\n"
        "$$\\|\\boldsymbol{x}\\|_1 = \\sum_i |x_i|$$\n\n"
        "它经常使用在需要**区分 0 和非 0 元素**的情形中。\n\n"
        "$L^0$ 范数：如果需要衡量向量中非 0 元素的个数，但**它并不是一个范数** (不满足三角不等式和数乘)，"
        "此时 $L^1$ 范数可以作为它的一个替代。\n\n"
        "$L^\\infty$ 范数：它在数学上是向量元素绝对值的最大值，因此也被叫做 (Max norm)：\n\n"
        "$$\\|\\boldsymbol{x}\\|_\\infty = \\max_i |x_i|$$\n\n"
        "有时我们想衡量一个矩阵，机器学习中通常使用的是 **F 范数 (Frobenius norm)**，其定义为：\n\n"
        "$$\\|\\boldsymbol{A}\\|_F = \\sqrt{\\sum_{i,j} A_{i,j}^2}$$",
        "# 花书原文配套代码：范数\n"
        "a = np.array([1.0, 3.0])\n"
        "print('向量 2 范数:', np.linalg.norm(a, ord=2))\n"
        "print('向量 1 范数:', np.linalg.norm(a, ord=1))\n"
        "print('向量无穷范数:', np.linalg.norm(a, ord=np.inf))\n\n"
        "M = np.array([[1.0, 3.0], [2.0, 1.0]])\n"
        "print('矩阵 F 范数:', np.linalg.norm(M, ord='fro'))"
    )

    b.md(        "### 3.7 范数 (norms)\n\n"
        "向量「长度」的推广。最常用三个：\n\n"
        "- **$L_1$ 范数**：$\\|\\mathbf{x}\\|_1 = \\sum_i |x_i|$\n"
        "- **$L_2$ 范数（欧氏）**：$\\|\\mathbf{x}\\|_2 = \\sqrt{\\sum_i x_i^2}$\n"
        "- **$L_\\infty$ 范数**：$\\|\\mathbf{x}\\|_\\infty = \\max_i |x_i|$\n"
        "- **Frobenius 范数（矩阵）**：$\\|\\mathbf{A}\\|_F = \\sqrt{\\sum_{i,j} A_{i,j}^2}$\n"
    )
    b.code(
        "x = np.array([3.0, -4.0])\n"
        "print('L1:', np.linalg.norm(x, ord=1))     # 7\n"
        "print('L2:', np.linalg.norm(x, ord=2))     # 5\n"
        "print('L∞:', np.linalg.norm(x, ord=np.inf))  # 4\n\n"
        "A = np.array([[3.0, 0.0], [4.0, 0.0]])\n"
        "print('Frobenius:', np.linalg.norm(A))      # 5"
    )

    # 3.E8
    b.md(
        "### ✏️ 例题 3.E8：手写 L2 范数\n\n"
        "不要用 `np.linalg.norm`，用基本运算实现。"
    )
    b.code(
        "def my_l2(x):\n"
        "    return np.sqrt(np.sum(x ** 2))\n\n"
        "x = np.array([3.0, 4.0, 12.0])\n"
        "checks.assert_close('L2', my_l2(x), np.linalg.norm(x))  # 13",
        work_src=(
            "def my_l2(x):\n"
            "    return np.sqrt(np.sum(___))\n\n"
            "x = np.array([3.0, 4.0, 12.0])\n"
            "checks.assert_close('L2', my_l2(x), np.linalg.norm(x))  # 13"
        )
    )

    # 3.8 eigendecomposition
    _yuanwen(
        b,
        "特征值分解",
        "如果一个 $n \\times n$ 矩阵 $\\boldsymbol{A}$ 有 $n$ 组线性无关的单位特征向量 "
        "$\\{\\boldsymbol{v}^{(1)}, \\ldots, \\boldsymbol{v}^{(n)}\\}$，"
        "以及对应的特征值 $\\lambda_1, \\ldots, \\lambda_n$。"
        "将这些特征向量按列拼接成一个矩阵："
        "$\\boldsymbol{V} = [\\boldsymbol{v}^{(1)}, \\ldots, \\boldsymbol{v}^{(n)}]$，"
        "并将对应的特征值拼接成一个向量：$\\boldsymbol{\\lambda} = [\\lambda_1, \\ldots, \\lambda_n]$。\n\n"
        "$\\boldsymbol{A}$ 的**特征值分解 (Eigendecomposition)** 为：\n\n"
        "$$\\boldsymbol{A} = \\boldsymbol{V} \\mathrm{diag}(\\boldsymbol{\\lambda}) \\boldsymbol{V}^{-1}$$\n\n"
        "**注意**：\n"
        "- 不是所有的矩阵都有特征值分解\n"
        "- 在某些情况下，实矩阵的特征值分解可能会得到复矩阵",
        "# 花书原文配套代码：特征分解\n"
        "A = np.array([[1.0, 2.0, 3.0],\n"
        "              [4.0, 5.0, 6.0],\n"
        "              [7.0, 8.0, 9.0]])\n"
        "print('特征值:', np.linalg.eigvals(A))\n"
        "eigvals, eigvectors = np.linalg.eig(A)\n"
        "print('特征值:', eigvals)\n"
        "print('特征向量:\\n', eigvectors)"
    )

    b.md(        "### 3.8 特征分解 (eigendecomposition)\n\n"
        "对**方阵** $\\mathbf{A}$，若存在非零向量 $\\mathbf{v}$ 和标量 $\\lambda$ 使得\n\n"
        "$$\\mathbf{A}\\mathbf{v} = \\lambda \\mathbf{v}$$\n\n"
        "则 $\\mathbf{v}$ 叫**特征向量**，$\\lambda$ 叫**特征值**。\n\n"
        "**几何直觉**：A 把 v 这个方向上的向量**只缩放、不旋转**，缩放倍数就是 λ。\n\n"
        "对称矩阵的特征值一定是实数、特征向量两两正交——这是 PCA 等算法的基础。\n"
    )
    b.code(
        "# 对角矩阵——特征值就是对角元，特征向量是基向量\n"
        "A = np.array([[3.0, 0.0], [0.0, 2.0]])\n"
        "vals, vecs = np.linalg.eig(A)\n"
        "print('eigenvalues :', vals)\n"
        "print('eigenvectors:', vecs, sep='\\n')\n\n"
        "# 验证 Av = λv\n"
        "for i in range(len(vals)):\n"
        "    v = vecs[:, i]\n"
        "    print(f'  A @ v_{i} = {A @ v}, λ_{i} * v_{i} = {vals[i] * v}')"
    )

    # 3.E9
    b.md(
        "### ✏️ 例题 3.E9：对称矩阵的特征向量正交\n\n"
        "造一个对称矩阵（`A = R + R.T` 的方法），验证它的特征向量两两正交。\n"
    )
    b.code(
        "R = np.random.randn(4, 4)\n"
        "A = R + R.T  # 对称化\n"
        "vals, vecs = np.linalg.eigh(A)  # eigh 专给对称/Hermitian 矩阵\n"
        "# 特征向量是 vecs 的列\n"
        "gram = vecs.T @ vecs  # 应该是单位矩阵（列两两正交且单位长）\n"
        "checks.assert_close('正交性 (vecs.T @ vecs == I)', gram, np.eye(4), tol=1e-6)\n"
        "print('gram 矩阵:', gram, sep='\\n')",
        work_src=(
            "R = np.random.randn(4, 4)\n"
            "A = R + R.T  # 对称化（为啥？想想 (R+R^T)^T = ?）\n"
            "vals, vecs = np.linalg.eigh(A)\n"
            "gram = ___  # 算 vecs 列两两点积矩阵\n"
            "checks.assert_close('正交性 (vecs.T @ vecs == I)', gram, np.eye(4), tol=1e-6)\n"
            "print('gram 矩阵:', gram, sep='\\n')"
        )
    )

    # 3.9 SVD
    _yuanwen(
        b,
        "奇异值分解 (SVD)",
        "**奇异值分解 (Singular Value Decomposition, SVD)** 提供了另一种分解矩阵的方式，"
        "将其分解为奇异向量和奇异值。\n\n"
        "与特征值分解相比，奇异值分解更加通用，"
        "**所有的实矩阵都可以进行奇异值分解，而特征值分解只对某些方阵可以**。\n\n"
        "奇异值分解的形式为：\n\n"
        "$$\\boldsymbol{A} = \\boldsymbol{U} \\boldsymbol{\\Sigma} \\boldsymbol{V}^\\top$$\n\n"
        "若 $\\boldsymbol{A}$ 是 $m \\times n$ 的，那么 $\\boldsymbol{U}$ 是 $m \\times m$ 的，"
        "其列向量称为**左奇异向量**，而 $\\boldsymbol{V}$ 是 $n \\times n$ 的，其列向量称为**右奇异向量**，"
        "而 $\\boldsymbol{\\Sigma}$ 是 $m \\times n$ 的一个对角矩阵，其对角元素称为矩阵 $\\boldsymbol{A}$ 的**奇异值**。\n\n"
        "事实上，**左奇异向量是 $\\boldsymbol{A}\\boldsymbol{A}^\\top$ 的特征向量，"
        "而右奇异向量是 $\\boldsymbol{A}^\\top\\boldsymbol{A}$ 的特征向量，"
        "非 0 奇异值的平方是 $\\boldsymbol{A}^\\top\\boldsymbol{A}$ 的非 0 特征值**。",
        "# 花书原文配套代码：SVD\n"
        "A = np.array([[1.0, 2.0, 3.0],\n"
        "              [4.0, 5.0, 6.0]])\n"
        "U, D, V = np.linalg.svd(A)\n"
        "print('U:\\n', U)\n"
        "print('D:', D)\n"
        "print('V:\\n', V)"
    )

    b.md(        "### 3.9 奇异值分解 SVD\n\n"
        "**对任意矩阵**（不需要方阵），都有：\n\n"
        "$$\\mathbf{A} = \\mathbf{U} \\boldsymbol{\\Sigma} \\mathbf{V}^\\top$$\n\n"
        "- $\\mathbf{U}$：$m \\times m$ 正交矩阵（左奇异向量）\n"
        "- $\\boldsymbol{\\Sigma}$：$m \\times n$ 「对角」矩阵，对角元 $\\sigma_1 \\ge \\sigma_2 \\ge \\cdots \\ge 0$（奇异值）\n"
        "- $\\mathbf{V}$：$n \\times n$ 正交矩阵（右奇异向量）\n\n"
        "**用途**：低秩近似（图像压缩）、PCA、矩阵伪逆、推荐系统。\n"
    )
    b.code(
        "A = np.array([[3.0, 1.0, 1.0], [-1.0, 3.0, 1.0]])\n"
        "U, S, Vt = np.linalg.svd(A, full_matrices=False)\n"
        "print('U shape:', U.shape, 'S:', S, 'Vt shape:', Vt.shape)\n\n"
        "# 重构 A\n"
        "A_reconstructed = U @ np.diag(S) @ Vt\n"
        "checks.assert_close('SVD 重构', A_reconstructed, A)\n"
        "print('reconstruct error:', np.linalg.norm(A - A_reconstructed))"
    )

    # 3.E10
    b.md(
        "### ✏️ 例题 3.E10：SVD 低秩近似\n\n"
        "随便造一个 6×6 矩阵 A，用前 2 个奇异值近似它，看误差。\n"
    )
    b.code(
        "np.random.seed(0)\n"
        "A = np.random.randn(6, 6)\n"
        "U, S, Vt = np.linalg.svd(A)\n"
        "k = 2  # 保留前 2 个奇异值\n"
        "A_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]\n"
        "err = np.linalg.norm(A - A_k)\n"
        "print(f'前 {k} 个奇异值: {S[:k]}')\n"
        "print(f'被丢弃的: {S[k:]}')\n"
        "print(f'重构误差 Frobenius: {err:.4f}')\n"
        "print(f'理论误差（被丢弃奇异值的平方和开根）: {np.sqrt((S[k:]**2).sum()):.4f}')",
        work_src=(
            "np.random.seed(0)\n"
            "A = np.random.randn(6, 6)\n"
            "U, S, Vt = np.linalg.svd(A)\n"
            "k = 2\n"
            "A_k = U[:, :___] @ np.diag(S[:___]) @ Vt[:___, :]\n"
            "err = np.linalg.norm(A - A_k)\n"
            "print(f'前 {k} 个奇异值: {S[:k]}')\n"
            "print(f'被丢弃的: {S[k:]}')\n"
            "print(f'重构误差: {err:.4f}')"
        )
    )


# ---------- Sec 4: 可视化 ----------

def ch02_sec4(b: Builder):
    b.md(
        "---\n\n## Sec 4 — 可视化\n\n"
        "看图比看公式直观得多。`utils/viz.py` 提供了几个 helper。\n"
    )

    # 4.1 vectors
    b.md("### 4.1 画 2D 向量")
    b.code(
        "vectors = np.array([[3, 1], [1, 2], [-2, 1]])\n"
        "fig, ax = viz.plot_vectors(vectors,\n"
        "                            labels=['v1', 'v2', 'v3'],\n"
        "                            title='2D 向量')"
    )

    # 4.E1
    b.md("### ✏️ 例题 4.E1：画两个互相垂直的向量")
    b.code(
        "v1 = np.array([3, 0])\n"
        "v2 = np.array([0, 3])\n"
        "# 验证：点积 = 0\n"
        "checks.assert_close('正交', np.dot(v1, v2), 0)\n"
        "viz.plot_vectors([v1, v2], labels=['v1', 'v2'], title='垂直向量');",
        work_src=(
            "v1 = np.array([___, ___])\n"
            "v2 = np.array([___, ___])\n"
            "# 验证点积 = 0（正交）\n"
            "checks.assert_close('正交', np.dot(v1, v2), 0)\n"
            "viz.plot_vectors([v1, v2], labels=['v1', 'v2'], title='垂直向量');"
        )
    )

    # 4.2 matrix action
    b.md(
        "### 4.2 矩阵作为线性变换\n\n"
        "**关键直觉**：一个 2×2 矩阵 $\\mathbf{A}$ 把单位圆变成椭圆。"
        "椭圆的长短轴方向 = 特征向量方向（对称矩阵情况）；长短轴长度 = 对应特征值。\n"
    )
    b.code(
        "# 旋转 + 缩放矩阵\n"
        "theta = np.deg2rad(30)\n"
        "R = np.array([[np.cos(theta), -np.sin(theta)],\n"
        "              [np.sin(theta),  np.cos(theta)]])\n"
        "S = np.diag([2.0, 0.5])\n"
        "A = R @ S\n"
        "viz.plot_matrix_action(A, title=f'A = R(30°) · diag(2, 0.5)');"
    )

    # 4.E2
    b.md(
        "### ✏️ 例题 4.E2：变化参数看几何效果\n\n"
        "把 $\\theta$ 改成 90°、把 diag 改成 `(3, 1)`，看椭圆怎么变。"
    )
    b.code(
        "theta = np.deg2rad(90)\n"
        "R = np.array([[np.cos(theta), -np.sin(theta)],\n"
        "              [np.sin(theta),  np.cos(theta)]])\n"
        "S = np.diag([3.0, 1.0])\n"
        "A = R @ S\n"
        "viz.plot_matrix_action(A, title=f'θ=90°, diag(3,1)');",
        work_src=(
            "theta = np.deg2rad(___)  # 改成你想看的角度\n"
            "R = np.array([[np.cos(theta), -np.sin(theta)],\n"
            "              [np.sin(theta),  np.cos(theta)]])\n"
            "S = np.diag([___, ___])\n"
            "A = R @ S\n"
            "viz.plot_matrix_action(A, title='自由发挥');"
        )
    )

    # 4.3 eigenvalues
    b.md("### 4.3 特征向量与特征值可视化")
    b.code(
        "# 对称矩阵：特征向量两两正交\n"
        "A = np.array([[3.0, 1.0], [1.0, 2.0]])\n"
        "viz.plot_eigen(A, title='对称矩阵的特征向量（红）');"
    )

    # 4.E3
    b.md(
        "### ✏️ 例题 4.E3：预测特征值的几何意义\n\n"
        "下面这个矩阵 $\\mathbf{A} = \\mathrm{diag}(2, 3)$ 是对角矩阵。"
        "**先猜**：它的特征值是几？特征向量沿哪个方向？再让代码验证。\n"
    )
    b.code(
        "A = np.diag([2.0, 3.0])\n"
        "vals, vecs = np.linalg.eig(A)\n"
        "print('特征值:', vals)         # 预测：[2, 3]\n"
        "print('特征向量:', vecs, sep='\\n')  # 预测：单位基向量\n"
        "viz.plot_eigen(A);"
    )

    # 4.4 tensor slices
    b.md("### 4.4 把 3 阶张量「摞」开看")
    b.code(
        "np.random.seed(1)\n"
        "T = np.random.randn(4, 5, 5)  # 4 张 5×5 矩阵摞起来\n"
        "viz.plot_tensor_slices(T, axis=0, title='3 阶张量沿 axis=0 切片');"
    )

    # 4.E4
    b.md(
        "### ✏️ 例题 4.E4：PCA 投影可视化\n\n"
        "造一个椭圆形点云（2D，但拉伸过），用 SVD 找它的主方向并投影到第一主成分。"
    )
    b.code(
        "np.random.seed(7)\n"
        "n = 200\n"
        "raw = np.random.randn(n, 2)\n"
        "# 拉伸 + 旋转\n"
        "stretch = np.diag([3.0, 0.5])\n"
        "theta = np.deg2rad(30)\n"
        "R = np.array([[np.cos(theta), -np.sin(theta)],\n"
        "              [np.sin(theta),  np.cos(theta)]])\n"
        "X = (raw @ stretch) @ R.T  # 形状 (n, 2)\n\n"
        "# PCA via SVD：先中心化\n"
        "X_centered = X - X.mean(axis=0)\n"
        "U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)\n"
        "pc1 = Vt[0]  # 第一主成分方向\n\n"
        "fig, ax = viz.plot_points_2d(X, c='steelblue', title='椭圆点云 + 主方向（红）')\n"
        "ax.quiver(0, 0, pc1[0] * 4, pc1[1] * 4,\n"
        "          angles='xy', scale_units='xy', scale=1,\n"
        "          color='red', width=0.012)\n"
        "print('第一主方向:', pc1)\n"
        "print('对应「重要度」（奇异值）:', S)"
    )

    # 4.E5: ipywidgets slider
    b.md(
        "### ✏️ 例题 4.E5（交互）：旋转角度滑块\n\n"
        "拖动滑块观察旋转矩阵作用下的椭圆怎么转。**注意**：交互 widget 第一次运行需要一两秒。\n"
    )
    b.code(
        "from ipywidgets import interact, FloatSlider\n\n"
        "def show_rotation(deg=30, sx=2.0, sy=0.5):\n"
        "    theta = np.deg2rad(deg)\n"
        "    R = np.array([[np.cos(theta), -np.sin(theta)],\n"
        "                  [np.sin(theta),  np.cos(theta)]])\n"
        "    A = R @ np.diag([sx, sy])\n"
        "    fig, ax = plt.subplots(figsize=(5, 5))\n"
        "    viz.plot_matrix_action(A, ax=ax, title=f'θ={deg}°  diag({sx}, {sy})')\n"
        "    plt.show()\n\n"
        "interact(show_rotation,\n"
        "         deg=FloatSlider(min=0, max=360, step=15, value=30),\n"
        "         sx=FloatSlider(min=0.2, max=4, step=0.2, value=2.0),\n"
        "         sy=FloatSlider(min=0.2, max=4, step=0.2, value=0.5));"
    )


# ---------- Sec 5: 与花书对照 ----------

def ch02_sec5(b: Builder):
    b.md(
        "---\n\n## Sec 5 — 与花书对照\n\n"
        "对照花书第二章（pp.27–34），把记号和我们这里写的对上。这一节不重复内容，"
        "只做「翻译表」和「延伸阅读」指引。\n\n"
        "### 5.1 记号速查\n\n"
        "| 对象 | 花书字体 | 元素 | 集合 |\n"
        "|------|---------|------|------|\n"
        "| 标量 | $a$（细斜体） | — | $\\mathbb{R}$ 或 $\\mathbb{N}$ |\n"
        "| 向量 | $\\mathbf{a}$（粗斜体小写） | $a_i$ | $\\mathbb{R}^n$ |\n"
        "| 矩阵 | $\\mathbf{A}$（粗体大写） | $A_{i,j}$ | $\\mathbb{R}^{m\\times n}$ |\n"
        "| 张量 | $\\mathsf{A}$（sans-serif 大写） | $\\mathsf{A}_{i,j,k}$ | $\\mathbb{R}^{n_1\\times\\cdots\\times n_k}$ |\n"
        "\n"
        "花书 p.28 把这套字体约定一一摆出来——光看字体就能认出对象是什么。\n"
    )
    b.md(
        "### 5.2 本章对应到花书的节\n\n"
        "| 我们 Sec | 花书章节 | 页码 |\n"
        "|---------|---------|------|\n"
        "| Sec 2.1（$\\mathbb{R}^n$） | 2.1 | p.27–28 |\n"
        "| Sec 3.2（转置） | 2.1 | p.29 |\n"
        "| Sec 3.3（Hadamard） | 2.2 | p.30 |\n"
        "| Sec 3.4（矩阵乘） | 2.2 | p.29–30 |\n"
        "| Sec 3.6（迹） | 2.10 | p.36 |\n"
        "| Sec 3.7（范数） | 2.5 | p.32 |\n"
        "| Sec 3.8（特征分解） | 2.7 | p.33 |\n"
        "| Sec 3.9（SVD） | 2.8 | p.34 |\n"
    )

    # 5.E1
    b.md(
        "### ✏️ 例题 5.E1：术语翻译\n\n"
        "花书原文用了几个英文术语，请把它们对到本章学到的概念："
    )
    b.code(
        "english_to_chinese = {\n"
        "    'transpose':       '转置',\n"
        "    'main diagonal':   '主对角线',\n"
        "    'broadcasting':    '广播（向量+矩阵自动复制）',\n"
        "    'matrix product':  '矩阵乘积',\n"
        "    'element-wise product': 'Hadamard 乘积（逐元素乘）',\n"
        "    'dot product':     '点积',\n"
        "    'norm':            '范数',\n"
        "    'eigendecomposition': '特征分解',\n"
        "    'singular value decomposition': '奇异值分解 (SVD)',\n"
        "}\n"
        "for en, zh in english_to_chinese.items():\n"
        "    print(f'  {en:30s} → {zh}')",
        work_src=(
            "english_to_chinese = {\n"
            "    'transpose':       '___',\n"
            "    'main diagonal':   '___',\n"
            "    'broadcasting':    '___',\n"
            "    'matrix product':  '___',\n"
            "    'element-wise product': '___',\n"
            "    'dot product':     '___',\n"
            "    'norm':            '___',\n"
            "    'eigendecomposition': '___',\n"
            "    'singular value decomposition': '___',\n"
            "}\n"
            "for en, zh in english_to_chinese.items():\n"
            "    print(f'  {en:30s} → {zh}')"
        )
    )

    # 5.E2
    b.md(
        "### ✏️ 例题 5.E2：花书 p.28 一句话翻译\n\n"
        "花书 p.28 的「张量」定义那一句话原文（仅短引用）：\n\n"
        "> 「在某些情况下，我们会讨论坐标超过两维的数组。」 — 花书 p.28\n\n"
        "用你自己的话**重新写一遍这句话**，并说说它跟 NumPy 里的 `.shape` 是什么关系。"
    )
    b.md("**示范回答**：当数据需要超过两个下标才能定位一个元素时，就升级成张量了。NumPy 用 shape 的「长度」反映阶数——比如 shape `(N, H, W, C)` 就是 4 阶张量。\n")


# ---------- Sec 6: 综合练习 ----------

def ch02_sec6(b: Builder):
    b.md(
        "---\n\n## Sec 6 — 综合练习\n\n"
        "把前面所有算子串起来，做几个「完整的小任务」。\n"
    )

    # 6.E1
    _yuanwen(
        b,
        "PCA (主成分分析)",
        "假设我们有 $m$ 个数据点 $\\boldsymbol{x}^{(1)}, \\ldots, \\boldsymbol{x}^{(m)} \\in \\mathbb{R}^n$，"
        "对于每个数据点 $\\boldsymbol{x}^{(i)}$，我们希望找到一个对应的点 "
        "$\\boldsymbol{c}^{(i)} \\in \\mathbb{R}^l, l < n$ 去表示它（相当于对它进行降维），"
        "并且让损失的信息尽可能地少。\n\n"
        "**编码-解码框架**：设编码 $f$ 和解码 $g$ 函数，"
        "有 $f(\\boldsymbol{x}) = \\boldsymbol{c},\\ \\boldsymbol{x} \\approx g(f(\\boldsymbol{x}))$。"
        "考虑一个线性解码函数 $g(\\boldsymbol{c}) = \\boldsymbol{D}\\boldsymbol{c},\\ "
        "\\boldsymbol{D} \\in \\mathbb{R}^{n \\times l}$，"
        "为了计算方便，将 $\\boldsymbol{D}$ 的列向量约束为相互正交，且具有单位范数（获取唯一解）。\n\n"
        "对于给定的 $\\boldsymbol{x}$，我们需要找到信息损失最小的 $\\boldsymbol{c}^*$，即求解：\n\n"
        "$$\\boldsymbol{c}^* = \\arg\\min_{\\boldsymbol{c}} \\|\\boldsymbol{x} - g(\\boldsymbol{c})\\|_2^2$$\n\n"
        "**推导链**（详见花书拆解 PDF 第 5–6 页）：\n\n"
        "1. 展开 $\\|\\boldsymbol{x} - g(\\boldsymbol{c})\\|_2^2 = \\boldsymbol{x}^\\top \\boldsymbol{x} - 2\\boldsymbol{x}^\\top g(\\boldsymbol{c}) + g(\\boldsymbol{c})^\\top g(\\boldsymbol{c})$\n"
        "2. 代入 $g(\\boldsymbol{c}) = \\boldsymbol{D}\\boldsymbol{c}$，利用约束 $\\boldsymbol{D}^\\top \\boldsymbol{D} = \\boldsymbol{I}_l$\n"
        "3. 对 $\\boldsymbol{c}$ 求梯度令其为零 → $\\boldsymbol{c} = \\boldsymbol{D}^\\top \\boldsymbol{x}$\n"
        "4. 因此**编码函数** $f(\\boldsymbol{x}) = \\boldsymbol{D}^\\top \\boldsymbol{x}$；"
        "重构为 $r(\\boldsymbol{x}) = \\boldsymbol{D}\\boldsymbol{D}^\\top \\boldsymbol{x}$\n"
        "5. 求最优 $\\boldsymbol{D}$（F 范数 + 拉格朗日乘子）：\n\n"
        "$$\\boldsymbol{D}^* = \\arg\\min_{\\boldsymbol{D}} \\sqrt{\\sum_{i,j} (x^{(i)}_j - r(\\boldsymbol{x}^{(i)})_j)^2},\\ \\mathrm{s.t.}\\ \\boldsymbol{D}^\\top \\boldsymbol{D} = \\boldsymbol{I}_l$$\n\n"
        "**关键结论**：\n\n"
        "> PCA 是通过线性变换找到一个 $\\mathrm{Var}[\\boldsymbol{c}]$ 是对角矩阵的表示 "
        "$\\boldsymbol{c} = \\boldsymbol{V}^\\top \\boldsymbol{x}$，"
        "矩阵 $\\boldsymbol{X}$ 的主成分可以通过奇异值分解 (SVD) 得到，"
        "也就是说**主成分是 $\\boldsymbol{X}$ 的右奇异向量**。\n\n"
        "数学推导（$\\boldsymbol{X}$ 已中心化，$\\mathbb{E}[\\boldsymbol{x}] = 0$，"
        "无偏协方差 $\\mathrm{Var}[\\boldsymbol{x}] = \\frac{1}{m-1} \\boldsymbol{X}^\\top \\boldsymbol{X}$）：\n\n"
        "假设 $\\boldsymbol{V}$ 是 $\\boldsymbol{X} = \\boldsymbol{U}\\boldsymbol{\\Sigma}\\boldsymbol{V}^\\top$ "
        "SVD 的右奇异向量，则：\n\n"
        "$$\\boldsymbol{X}^\\top \\boldsymbol{X} = "
        "(\\boldsymbol{U}\\boldsymbol{\\Sigma}\\boldsymbol{V}^\\top)^\\top "
        "\\boldsymbol{U}\\boldsymbol{\\Sigma}\\boldsymbol{V}^\\top "
        "= \\boldsymbol{V}\\boldsymbol{\\Sigma}^\\top \\boldsymbol{U}^\\top "
        "\\boldsymbol{U}\\boldsymbol{\\Sigma}\\boldsymbol{V}^\\top "
        "= \\boldsymbol{V}\\boldsymbol{\\Sigma}^2 \\boldsymbol{V}^\\top$$\n\n"
        "因此 $\\boldsymbol{c} = \\boldsymbol{V}^\\top \\boldsymbol{x}$ 的协方差是对角的，"
        "分量之间彼此线性无关。下面 Sec 6 的例题就是动手用 SVD 把这条推导跑出来。"
    )

    b.md(        "### ✏️ 例题 6.E1：成对向量夹角\n\n"
        "两组向量 $\\mathbf{a}_1, \\ldots, \\mathbf{a}_m \\in \\mathbb{R}^d$ 和 $\\mathbf{b}_1, \\ldots, \\mathbf{b}_n \\in \\mathbb{R}^d$，"
        "求 $m \\times n$ 矩阵 $\\mathbf{C}$，其中 $C_{i,j} = \\cos(\\angle(\\mathbf{a}_i, \\mathbf{b}_j))$。\n\n"
        "提示：$\\cos\\theta = \\dfrac{\\mathbf{a}\\cdot\\mathbf{b}}{\\|\\mathbf{a}\\|\\|\\mathbf{b}\\|}$。\n"
    )
    b.code(
        "def cosine_matrix(A, B):\n"
        "    '''A: (m, d), B: (n, d) → returns (m, n) cosine sim.'''\n"
        "    A_norm = A / np.linalg.norm(A, axis=1, keepdims=True)\n"
        "    B_norm = B / np.linalg.norm(B, axis=1, keepdims=True)\n"
        "    return A_norm @ B_norm.T\n\n"
        "A = np.array([[1, 0, 0], [0, 1, 0]])\n"
        "B = np.array([[1, 0, 0], [1, 1, 0], [0, 0, 1]])\n"
        "C = cosine_matrix(A, B)\n"
        "expected = np.array([[1.0, 1/np.sqrt(2), 0.0],\n"
        "                     [0.0, 1/np.sqrt(2), 0.0]])\n"
        "checks.assert_close('cosine matrix', C, expected)\n"
        "print(C)",
        work_src=(
            "def cosine_matrix(A, B):\n"
            "    '''A: (m, d), B: (n, d) → returns (m, n) cosine sim.'''\n"
            "    A_norm = A / np.linalg.norm(A, axis=___, keepdims=True)\n"
            "    B_norm = B / np.linalg.norm(B, axis=___, keepdims=True)\n"
            "    return A_norm @ ___  # 提示：让结果是 (m, n)\n\n"
            "A = np.array([[1, 0, 0], [0, 1, 0]])\n"
            "B = np.array([[1, 0, 0], [1, 1, 0], [0, 0, 1]])\n"
            "C = cosine_matrix(A, B)\n"
            "expected = np.array([[1.0, 1/np.sqrt(2), 0.0],\n"
            "                     [0.0, 1/np.sqrt(2), 0.0]])\n"
            "checks.assert_close('cosine matrix', C, expected)\n"
            "print(C)"
        )
    )

    # 6.E2 manual PCA
    b.md(
        "### ✏️ 例题 6.E2：手写 PCA\n\n"
        "给数据矩阵 $\\mathbf{X} \\in \\mathbb{R}^{n \\times d}$（n 个 d 维点），"
        "求前 $k$ 个主成分方向（按方差递减），并把数据投影到 $k$ 维。\n\n"
        "步骤：\n"
        "1. 中心化：减去每列均值\n"
        "2. SVD：$\\mathbf{X}_c = \\mathbf{U}\\boldsymbol{\\Sigma}\\mathbf{V}^\\top$\n"
        "3. 主方向 = $\\mathbf{V}$ 的前 $k$ 列\n"
        "4. 投影：$\\mathbf{Z} = \\mathbf{X}_c \\mathbf{V}_{[:,:k]}$\n"
    )
    b.code(
        "def pca(X, k):\n"
        "    X_centered = X - X.mean(axis=0)\n"
        "    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)\n"
        "    V = Vt.T\n"
        "    components = V[:, :k]      # (d, k)\n"
        "    projected = X_centered @ components  # (n, k)\n"
        "    return projected, components, S[:k]\n\n"
        "np.random.seed(0)\n"
        "X = np.random.randn(50, 5) @ np.diag([5, 3, 1, 0.5, 0.1])\n"
        "Z, V_k, sigmas = pca(X, k=2)\n"
        "print('原维度:', X.shape[1], '降到:', Z.shape[1])\n"
        "print('保留奇异值:', sigmas)\n"
        "checks.assert_shape('PCA 投影 shape', Z, (50, 2))",
        work_src=(
            "def pca(X, k):\n"
            "    X_centered = X - X.mean(axis=___)  # 沿哪条轴算均值？\n"
            "    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)\n"
            "    V = ___  # Vt 转置\n"
            "    components = V[:, :___]\n"
            "    projected = X_centered @ ___\n"
            "    return projected, components, S[:k]\n\n"
            "np.random.seed(0)\n"
            "X = np.random.randn(50, 5) @ np.diag([5, 3, 1, 0.5, 0.1])\n"
            "Z, V_k, sigmas = pca(X, k=2)\n"
            "print('原维度:', X.shape[1], '降到:', Z.shape[1])\n"
            "print('保留奇异值:', sigmas)\n"
            "checks.assert_shape('PCA 投影 shape', Z, (50, 2))"
        )
    )

    # 6.E3 SVD compression of an image-like matrix
    b.md(
        "### ✏️ 例题 6.E3：SVD 压缩「图像」\n\n"
        "造一张 64×64 的「渐变 + 噪声」图，用前 $k=10$ 个奇异值近似它，看压缩效果。"
    )
    b.code(
        "# 构造图：渐变 + 噪声\n"
        "x = np.linspace(-1, 1, 64)\n"
        "X, Y = np.meshgrid(x, x)\n"
        "img = np.sin(3 * X) * np.cos(2 * Y) + 0.1 * np.random.randn(64, 64)\n\n"
        "U, S, Vt = np.linalg.svd(img, full_matrices=False)\n\n"
        "fig, axes = plt.subplots(1, 4, figsize=(14, 4))\n"
        "axes[0].imshow(img, cmap='gray');         axes[0].set_title('原图 (64x64)')\n"
        "for ax_idx, k in enumerate([2, 10, 30], start=1):\n"
        "    img_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]\n"
        "    axes[ax_idx].imshow(img_k, cmap='gray')\n"
        "    axes[ax_idx].set_title(f'前 {k} 个奇异值')\n"
        "for ax in axes:\n"
        "    ax.set_xticks([]); ax.set_yticks([])\n"
        "plt.tight_layout(); plt.show()"
    )

    # 6.E4 verify identity
    b.md(
        "### ✏️ 例题 6.E4：恒等式验证 $(\\mathbf{AB})^\\top = \\mathbf{B}^\\top \\mathbf{A}^\\top$\n\n"
        "花书 p.30 式 (2.9)。用随机矩阵验证一下。"
    )
    b.code(
        "A = np.random.randn(3, 4)\n"
        "B = np.random.randn(4, 5)\n"
        "lhs = (A @ B).T\n"
        "rhs = B.T @ A.T\n"
        "checks.assert_close('(AB)^T == B^T A^T', lhs, rhs)\n"
        "print('两边形状:', lhs.shape, rhs.shape)",
        work_src=(
            "A = np.random.randn(3, 4)\n"
            "B = np.random.randn(4, 5)\n"
            "lhs = ___    # (AB)^T\n"
            "rhs = ___    # B^T A^T\n"
            "checks.assert_close('(AB)^T == B^T A^T', lhs, rhs)\n"
            "print('两边形状:', lhs.shape, rhs.shape)"
        )
    )

    # 6.E5 sum of squares via trace
    b.md(
        "### ✏️ 例题 6.E5：用迹算 Frobenius 范数平方\n\n"
        "证明（用代码验证）：$\\|\\mathbf{A}\\|_F^2 = \\mathrm{tr}(\\mathbf{A}^\\top \\mathbf{A})$。"
    )
    b.code(
        "A = np.random.randn(5, 7)\n"
        "frob_sq_direct = (A ** 2).sum()\n"
        "frob_sq_trace = np.trace(A.T @ A)\n"
        "checks.assert_close('||A||_F^2 == tr(A^T A)', frob_sq_direct, frob_sq_trace)\n"
        "print(f'直接算: {frob_sq_direct:.4f}, trace 算: {frob_sq_trace:.4f}')"
    )

    # 6.E6 angles between basis vectors after rotation
    b.md(
        "### ✏️ 例题 6.E6：旋转保持角度\n\n"
        "旋转矩阵 $\\mathbf{R}$ 满足 $\\mathbf{R}^\\top \\mathbf{R} = \\mathbf{I}$（正交）。"
        "这意味着 $\\mathbf{R}$ 不改变向量之间的角度。验证。"
    )
    b.code(
        "theta = np.deg2rad(37)\n"
        "R = np.array([[np.cos(theta), -np.sin(theta)],\n"
        "              [np.sin(theta),  np.cos(theta)]])\n"
        "checks.assert_close('R^T R == I', R.T @ R, np.eye(2))\n\n"
        "v1 = np.array([1.0, 2.0])\n"
        "v2 = np.array([3.0, -1.0])\n"
        "cos_before = v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2))\n"
        "rv1, rv2 = R @ v1, R @ v2\n"
        "cos_after = rv1 @ rv2 / (np.linalg.norm(rv1) * np.linalg.norm(rv2))\n"
        "checks.assert_close('角度保持', cos_before, cos_after)"
    )

    # 6.E7 image flattening + dot product
    b.md(
        "### ✏️ 例题 6.E7：把图像当向量做相似度\n\n"
        "造 3 张 8×8 的随机灰度图，展平后两两算余弦相似度。"
    )
    b.code(
        "np.random.seed(2)\n"
        "imgs = np.random.randn(3, 8, 8)\n"
        "flat = imgs.reshape(3, -1)  # (3, 64)\n"
        "cos_mat = cosine_matrix(flat, flat)  # 重用 6.E1 的函数\n"
        "print('两两余弦相似度矩阵:', cos_mat, sep='\\n')\n"
        "checks.assert_close('对角线为 1', np.diag(cos_mat), np.ones(3))",
        work_src=(
            "np.random.seed(2)\n"
            "imgs = np.random.randn(3, 8, 8)\n"
            "flat = imgs.reshape(3, ___)  # 把 8x8 展平为长度 64 的向量\n"
            "cos_mat = cosine_matrix(flat, flat)  # 重用 6.E1 的函数\n"
            "print('两两余弦相似度矩阵:', cos_mat, sep='\\n')\n"
            "checks.assert_close('对角线为 1', np.diag(cos_mat), np.ones(3))"
        )
    )

    # 6.E8 einsum bridge
    b.md(
        "### ✏️ 例题 6.E8：用 einsum 写矩阵乘\n\n"
        "把矩阵乘用 Einstein 求和约定写出来（参考 vault notio "
        "[Einstein 求和约定](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2FEinstein%20%E6%B1%82%E5%92%8C%E7%BA%A6%E5%AE%9A)）"
    )
    b.code(
        "A = np.random.randn(3, 4)\n"
        "B = np.random.randn(4, 5)\n"
        "# 矩阵乘：C_{ij} = sum_k A_{ik} B_{kj}\n"
        "C_einsum = np.einsum('ik,kj->ij', A, B)\n"
        "C_at     = A @ B\n"
        "checks.assert_close('einsum == @', C_einsum, C_at)\n"
        "print('一致。einsum 字符串就是公式的字面翻译。')",
        work_src=(
            "A = np.random.randn(3, 4)\n"
            "B = np.random.randn(4, 5)\n"
            "# 填空：用 einsum 写矩阵乘（公式 C_{ij} = Σ_k A_{ik} B_{kj}）\n"
            "C_einsum = np.einsum('___', A, B)\n"
            "C_at     = A @ B\n"
            "checks.assert_close('einsum == @', C_einsum, C_at)"
        )
    )


# ---------- Sec 7: 自由探索 ----------

def ch02_sec7(b: Builder):
    b.md(
        "---\n\n## Sec 7 — 自由探索\n\n"
        "下面三个开放题没有标准答案。挑一两个写写——这是这一章最值钱的部分。\n"
    )
    b.md(
        "### ✏️ 任务 7.T1：对称矩阵特征值为啥都是实数？\n\n"
        "构造若干个对称矩阵（用 `R + R.T` 这招），把 `np.linalg.eig` 算出的特征值 dtype 都打印出来。"
        "再构造几个**非**对称矩阵看看差别。\n\n"
        "**思考**：能不能给出一个非对称矩阵特征值是复数的小例子？\n"
    )
    b.code("# 你的代码")

    b.md(
        "### ✏️ 任务 7.T2：构造一个让 PCA 「失效」的数据集\n\n"
        "PCA 假设方向「重要度」由方差衡量。"
        "请构造一个 2D 数据集，让 PCA 第一主方向**不是**人眼看上去的「主要方向」。\n\n"
        "提示：可以试一字形（直线上加少量正交噪声）vs 同心圆（方差全方向相同）。\n"
    )
    b.code("# 你的代码")

    b.md(
        "### ✏️ 任务 7.T3：用 SVD 给真实图压缩\n\n"
        "选一张方形小图（自己拍的、网上找的都行；64-128 像素方便），转灰度后做 SVD，"
        "看保留前 $k = 1, 5, 20, 50$ 个奇异值时图像的视觉质量变化。\n\n"
        "**进阶**：算「压缩比」——原图 $n^2$ 个数，秩-$k$ 近似需要存 $k(2n+1)$ 个数（$U, S, V^\\top$ 的相关切片），"
        "什么 $k$ 时压缩有意义？\n"
    )
    b.code("# 你的代码")


# ---------- Sec 8: 后面章节怎么再用本章工具（轻量预告） ----------

def ch02_sec8(b: Builder):
    b.md(
        "---\n\n## Sec 8 — 后面章节会怎么再用本章的工具（轻量预告）\n\n"
        "你已经把花书第 2 章的线性代数工具走了一遍。这一节**不教新东西**——\n"
        "只是给每个工具贴一个**轻量预告**：「这个东西，后续章节会怎么用」。\n\n"
        "**别担心听不懂**——预告就是预告，等你学到对应章节再回来看，那时会发现「Ch 2 里我就用过它」。\n\n"
        "> 这一节的所有例题只用你**已经学过**的 Ch 2 工具（向量、矩阵、张量、范数、矩阵乘、SVD）。\n"
        "> 不需要先懂梯度、softmax、神经网络——那些是后面章节的事。\n"
    )

    # ---- 8.1 范数 → 后面会用作「拉住参数」+「稀疏」 ----
    b.md(
        "### 8.1 范数：后面会用作「拉住参数」+「稀疏」的工具\n\n"
        "**回忆 Sec 3.7 + 原文 §7**：\n"
        "- $L^2$ 范数 = 向量到原点的欧氏距离（几何上是「长度」）\n"
        "- $L^1$ 范数 = 各分量绝对值之和（在原点附近增长比 $L^2$ 快）\n"
        "- $L^\\infty$ 范数 = 各分量绝对值的最大值\n\n"
        "**📍 后续怎么用（只需要看个名字）**：\n\n"
        "| 范数 | 后续章节会拿它干啥 | 在哪学 |\n"
        "|------|------------------|--------|\n"
        "| $L^2$ 范数 | 加到 loss 里防止参数太大，叫 **weight decay** | 花书 Ch 7 |\n"
        "| $L^1$ 范数 | 加到 loss 里让参数变**稀疏**（很多分量是 0） | 花书 Ch 7 |\n"
        "| $L^\\infty$ 范数 | 衡量「最坏情况下能错多远」 | Ch 7 + 鲁棒优化 |\n\n"
        "**Ch 2 阶段你只要知道**：范数衡量向量的「大小」，不同范数衡量得不一样。\n"
        "等学到 Ch 7 再看它们怎么变成 loss 项。\n"
    )

    # 8.E1
    b.md(
        "### ✏️ 例题 8.E1：三个向量，哪个范数大？\n\n"
        "给定三个向量：$\\boldsymbol{a} = [3, 4]$, $\\boldsymbol{b} = [5, 0]$, $\\boldsymbol{c} = [1, 1, 1, 1, 1]$。\n\n"
        "**先猜**：\n"
        "1. 哪个 $L^2$ 范数最大？\n"
        "2. 哪个 $L^1$ 范数最大？\n"
        "3. 哪个 $L^\\infty$ 范数最大？\n\n"
        "**再算 + 验证**——用 `np.linalg.norm(arr, ord=2/1/np.inf)`。\n"
    )
    b.code(
        "a = np.array([3, 4])\n"
        "b = np.array([5, 0])\n"
        "c = np.array([1, 1, 1, 1, 1])\n\n"
        "for name, x in [('a', a), ('b', b), ('c', c)]:\n"
        "    print(f'{name}: L1={np.linalg.norm(x, ord=1):.2f}  '\n"
        "          f'L2={np.linalg.norm(x, ord=2):.2f}  '\n"
        "          f'L∞={np.linalg.norm(x, ord=np.inf):.2f}')\n\n"
        "# 自检：算几个具体值\n"
        "checks.assert_close('8.E1 a 的 L2', np.linalg.norm(a, ord=2), 5.0)\n"
        "checks.assert_close('8.E1 c 的 L1', np.linalg.norm(c, ord=1), 5.0)\n"
        "checks.assert_close('8.E1 b 的 L∞', np.linalg.norm(b, ord=np.inf), 5.0)"
    )

    # ---- 8.2 矩阵乘法 → 神经网络一层 y = Wx + b ----
    b.md(
        "### 8.2 矩阵乘法：神经网络一层就是 $\\boldsymbol{y} = \\boldsymbol{W}\\boldsymbol{x} + \\boldsymbol{b}$\n\n"
        "**回忆 Sec 3.4 + 原文 §4**：矩阵乘法的形状规则是 $(m, n) \\times (n, p) = (m, p)$。\n\n"
        "**📍 后续怎么用**：神经网络最基础的一层（全连接层 / Linear / Dense）做的事就是：\n\n"
        "$$\\boldsymbol{y} = \\boldsymbol{W}\\boldsymbol{x} + \\boldsymbol{b}$$\n\n"
        "- $\\boldsymbol{x}$ 是输入向量，形状 $(d_{\\text{in}},)$\n"
        "- $\\boldsymbol{W}$ 是权重矩阵，形状 $(d_{\\text{out}}, d_{\\text{in}})$\n"
        "- $\\boldsymbol{b}$ 是 bias 向量，形状 $(d_{\\text{out}},)$\n"
        "- $\\boldsymbol{y}$ 是输出向量，形状 $(d_{\\text{out}},)$\n\n"
        "**只是一次矩阵乘 + 一次加法**——花书 Ch 6 学神经网络时第一个公式就是它，那时回来看就秒懂。\n\n"
        "Ch 2 阶段你只需练「形状传递」：输入是 $(d_{\\text{in}},)$，乘上 $(d_{\\text{out}}, d_{\\text{in}})$ 的 W，输出是 $(d_{\\text{out}},)$。\n"
        "**多层堆叠时**，前一层的输出 = 后一层的输入。\n"
    )

    # 8.E2
    b.md(
        "### ✏️ 例题 8.E2：堆 3 层的形状流水线\n\n"
        "假设你有 3 个全连接层，权重矩阵形状分别是：\n"
        "- 层 1: $\\boldsymbol{W}_1$ 形状 $(8, 4)$\n"
        "- 层 2: $\\boldsymbol{W}_2$ 形状 $(16, 8)$\n"
        "- 层 3: $\\boldsymbol{W}_3$ 形状 $(3, 16)$\n\n"
        "把一个 4 维向量 $\\boldsymbol{x}$ 依次过这 3 层（$\\boldsymbol{y} = \\boldsymbol{W}\\boldsymbol{x}$，先不管 bias），"
        "**先在纸上猜**每一层之后输出的 shape，再用 NumPy 算出来。\n\n"
        "**提示**：每一层都是 `W @ x`——`@` 是矩阵乘；形状规则是 $(m, n) \\times (n,) = (m,)$。\n"
    )
    b.code(
        "np.random.seed(0)\n"
        "x = np.random.randn(4)        # 输入 (4,)\n"
        "W1 = np.random.randn(8, 4)\n"
        "W2 = np.random.randn(16, 8)\n"
        "W3 = np.random.randn(3, 16)\n\n"
        "h1 = W1 @ x   # 层 1 输出\n"
        "h2 = W2 @ h1  # 层 2 输出\n"
        "h3 = W3 @ h2  # 层 3 输出（最终）\n\n"
        "print('x  shape:', x.shape)\n"
        "print('h1 shape:', h1.shape)\n"
        "print('h2 shape:', h2.shape)\n"
        "print('h3 shape:', h3.shape)\n\n"
        "checks.assert_shape('8.E2 层 1 输出', h1, (8,))\n"
        "checks.assert_shape('8.E2 层 2 输出', h2, (16,))\n"
        "checks.assert_shape('8.E2 最终输出', h3, (3,))",
        work_src=(
            "np.random.seed(0)\n"
            "x = np.random.randn(4)        # 输入 (4,)\n"
            "W1 = np.random.randn(8, 4)\n"
            "W2 = np.random.randn(16, 8)\n"
            "W3 = np.random.randn(3, 16)\n\n"
            "# 用 @ 把 x 顺序过 3 层\n"
            "h1 = ___\n"
            "h2 = ___\n"
            "h3 = ___\n\n"
            "print('x  shape:', x.shape)\n"
            "print('h1 shape:', h1.shape)\n"
            "print('h2 shape:', h2.shape)\n"
            "print('h3 shape:', h3.shape)\n\n"
            "checks.assert_shape('8.E2 层 1 输出', h1, (8,))\n"
            "checks.assert_shape('8.E2 层 2 输出', h2, (16,))\n"
            "checks.assert_shape('8.E2 最终输出', h3, (3,))"
        )
    )

    # ---- 8.3 SVD → 后面微调大模型时再相遇（LoRA） ----
    b.md(
        "### 8.3 SVD：后面微调大模型时会再相遇\n\n"
        "**回忆 Sec 3.9 + Sec 6 + 原文 §9/§10**：SVD 可以把矩阵分解成 "
        "$\\boldsymbol{A} = \\boldsymbol{U} \\boldsymbol{\\Sigma} \\boldsymbol{V}^\\top$，"
        "保留前 $k$ 个奇异值就能做**低秩近似**——PCA 就是这条。\n\n"
        "**📍 后续怎么用（只需要看个名字）**：训练好的大语言模型，权重矩阵 $\\boldsymbol{W}$ 的「有效秩」"
        "经常**远低于**它的形状给出的秩。等你学到大模型微调阶段，会遇到一个叫 **LoRA** 的技术——\n"
        "它的核心思想就是「权重的更新 $\\Delta \\boldsymbol{W}$ 可以用低秩矩阵近似」，本质是 Ch 2 你已经学过的 SVD 思想。\n\n"
        "**Ch 2 阶段你只需练**：用 SVD 给一个矩阵做秩-$k$ 近似，看 $k$ 越大重构越准。等学到大模型微调再深入。\n"
    )

    # 8.E3
    b.md(
        "### ✏️ 例题 8.E3：用 SVD 做不同秩的近似\n\n"
        "构造一个 $(50, 30)$ 的随机矩阵 $\\boldsymbol{A}$，分别做秩-5 和秩-20 的 SVD 近似，"
        "**比较重构误差**（用 Frobenius 范数 $\\|\\boldsymbol{A} - \\hat{\\boldsymbol{A}}_k\\|_F$）。\n\n"
        "**先猜**：秩-20 的误差应该比秩-5 的**大**还是**小**？\n\n"
        "**提示**：\n"
        "- `U, S, Vt = np.linalg.svd(A, full_matrices=False)` 得到紧凑 SVD\n"
        "- 秩-$k$ 近似：`A_k = U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]`\n"
        "- F 范数：`np.linalg.norm(matrix, ord='fro')`\n"
    )
    b.code(
        "np.random.seed(42)\n"
        "A = np.random.randn(50, 30)\n"
        "U, S, Vt = np.linalg.svd(A, full_matrices=False)\n\n"
        "def rank_k_approx(U, S, Vt, k):\n"
        "    return U[:, :k] @ np.diag(S[:k]) @ Vt[:k, :]\n\n"
        "A_5  = rank_k_approx(U, S, Vt, 5)\n"
        "A_20 = rank_k_approx(U, S, Vt, 20)\n\n"
        "err_5  = np.linalg.norm(A - A_5,  ord='fro')\n"
        "err_20 = np.linalg.norm(A - A_20, ord='fro')\n"
        "print(f'rank-5  重构误差 (F 范数): {err_5:.3f}')\n"
        "print(f'rank-20 重构误差 (F 范数): {err_20:.3f}')\n"
        "print(f'rank-30 (满秩，应该 ≈ 0): {np.linalg.norm(A - rank_k_approx(U, S, Vt, 30), ord=\"fro\"):.6f}')\n\n"
        "checks.assert_true('8.E3 秩越高误差越小', err_20 < err_5,\n"
        "                   hint=f'rank-20 误差 {err_20:.3f} 应该 < rank-5 误差 {err_5:.3f}')",
        work_src=(
            "np.random.seed(42)\n"
            "A = np.random.randn(50, 30)\n"
            "U, S, Vt = np.linalg.svd(A, full_matrices=False)\n\n"
            "def rank_k_approx(U, S, Vt, k):\n"
            "    # 秩-k 近似 = U 前 k 列 × diag(S 前 k 个) × Vt 前 k 行\n"
            "    return ___\n\n"
            "A_5  = rank_k_approx(U, S, Vt, 5)\n"
            "A_20 = rank_k_approx(U, S, Vt, 20)\n\n"
            "err_5  = np.linalg.norm(A - A_5,  ord='fro')\n"
            "err_20 = np.linalg.norm(A - A_20, ord='fro')\n"
            "print(f'rank-5  重构误差 (F 范数): {err_5:.3f}')\n"
            "print(f'rank-20 重构误差 (F 范数): {err_20:.3f}')\n\n"
            "checks.assert_true('8.E3 秩越高误差越小', err_20 < err_5,\n"
            "                   hint=f'rank-20 误差 {err_20:.3f} 应该 < rank-5 误差 {err_5:.3f}')"
        )
    )

    # ---- 8.4 张量阶 → 真实数据 / 模型代码的「形状语言」 ----
    b.md(
        "### 8.4 张量阶：读懂真实数据 + 模型代码的「形状语言」\n\n"
        "**回忆 Sec 1 + 原文 §1**：张量是「需要 $\\geq 3$ 个下标才能定位元素」的数组。\n\n"
        "**📍 后续怎么用**：你看深度学习的代码时，**第一道门**就是「这个 shape 在说什么」。\n"
        "下面这张表是后续章节最常见的真实数据形状——**学完 Ch 2 你已经能看懂全部**：\n\n"
        "| 数据 | 典型 shape | 阶 | 各维含义 |\n"
        "|------|-----------|----|----------|\n"
        "| 单张灰度图 | $(H, W)$ | 2 | 高、宽 |\n"
        "| 单张彩图 | $(H, W, 3)$ | 3 | 高、宽、RGB |\n"
        "| 一批彩图 | $(B, H, W, 3)$ | 4 | batch、高、宽、RGB |\n"
        "| 一段 token 序列 | $(T,)$ | 1 | 序列长度 |\n"
        "| 一批 token 序列 | $(B, T)$ | 2 | batch、序列长度 |\n"
        "| 一批 token + embedding | $(B, T, d)$ | 3 | batch、序列长度、每 token 的嵌入维 |\n"
        "| 一段音频 | $(T, C)$ | 2 | 时间、通道数 |\n\n"
        "**Ch 2 阶段你只要练**：拿到一个 shape 元组，能立刻在心里讲出每维是什么意思。\n"
    )

    # 8.E4
    b.md(
        "### ✏️ 例题 8.E4：读一个 batch 张量的「形状语言」\n\n"
        "假设你有一个**一批彩色图片**的 batch tensor，shape 是 $(4, 32, 32, 3)$。\n\n"
        "**先在纸上回答**：\n"
        "1. 这个 batch 里有几张图？\n"
        "2. 每张图的高、宽各是多少？\n"
        "3. 每个像素有几个数（通道）？\n"
        "4. 你怎么取出**第 0 张图**？shape 是多少？\n"
        "5. 你怎么取出**第 0 张图的 R 通道**？shape 是多少？\n\n"
        "**提示**：NumPy 切片用 `[..., k]` 取最后一维的第 $k$ 个；`batch[i]` 是 `batch[i, :, :, :]` 的简写。\n"
    )
    b.code(
        "np.random.seed(0)\n"
        "batch = np.random.rand(4, 32, 32, 3)   # 4 张 32×32 彩图\n\n"
        "img0 = batch[0]              # 第 0 张图\n"
        "img0_R = batch[0, :, :, 0]   # 第 0 张图的 R 通道\n\n"
        "print('batch  shape:', batch.shape)\n"
        "print('img0   shape:', img0.shape)\n"
        "print('img0_R shape:', img0_R.shape)\n\n"
        "checks.assert_shape('8.E4 batch',  batch,  (4, 32, 32, 3))\n"
        "checks.assert_shape('8.E4 img0',   img0,   (32, 32, 3))\n"
        "checks.assert_shape('8.E4 img0_R', img0_R, (32, 32))",
        work_src=(
            "np.random.seed(0)\n"
            "batch = np.random.rand(4, 32, 32, 3)\n\n"
            "img0   = ___              # 取出第 0 张图\n"
            "img0_R = ___              # 取出第 0 张图的 R 通道\n\n"
            "print('batch  shape:', batch.shape)\n"
            "print('img0   shape:', img0.shape)\n"
            "print('img0_R shape:', img0_R.shape)\n\n"
            "checks.assert_shape('8.E4 batch',  batch,  (4, 32, 32, 3))\n"
            "checks.assert_shape('8.E4 img0',   img0,   (32, 32, 3))\n"
            "checks.assert_shape('8.E4 img0_R', img0_R, (32, 32))"
        )
    )

    # 收尾
    b.md(
        "---\n\n"
        "### 🎯 Sec 8 小结\n\n"
        "本章学完后，你脑子里应该有这张「桥接表」：\n\n"
        "| 本章学到 | 后面哪一章会再用 | 起的什么角色 |\n"
        "|---------|---------------|-------------|\n"
        "| $L^2$ / $L^1$ 范数 | Ch 7 正则化 | weight decay / 稀疏 |\n"
        "| 矩阵乘 + 加法 | Ch 6 神经网络 | 一层 = `y = Wx + b` |\n"
        "| SVD 低秩近似 | 后续大模型微调 | LoRA 的数学根基 |\n"
        "| 张量阶 + shape | 每章看代码 | 「这个形状在说什么」 |\n\n"
        "**还记不清就回去看对应的 Sec 8.X**——这张表是你之后翻代码、读论文的一张「索引卡」。\n"
    )


# ---------- CHECKPOINT ----------

def ch02_checkpoint(b: Builder):
    b.md(
        "---\n\n## CHECKPOINT — 本章自检\n\n"
        "在下面打勾（双击 cell 进编辑模式，把 `[ ]` 改成 `[x]`）：\n\n"
        "**Ch 2 核心**（Sec 0–7 + 嵌入的花书原文 §1–§9）\n\n"
        "- [ ] 能熟练用 Jupyter 的 6 个核心快捷键\n"
        "- [ ] 能解释 cell 显示顺序 ≠ 执行顺序\n"
        "- [ ] 看到 shape 元组，能立刻说出阶数和每维含义\n"
        "- [ ] 能用自己的话区分 $\\mathbb{R}^{4\\times 4}$（2 阶）和 $\\mathbb{R}^{2\\times 2\\times 2\\times 2}$（4 阶）\n"
        "- [ ] 能用 NumPy 一行实现：转置、矩阵乘、Hadamard、点积、迹、范数、特征分解、SVD\n"
        "- [ ] 能记住 `A * B` 是 Hadamard，`A @ B` 是矩阵乘\n"
        "- [ ] 能解释为什么 $(\\mathbf{AB})^\\top = \\mathbf{B}^\\top \\mathbf{A}^\\top$（顺序反转）\n"
        "- [ ] 能用 SVD 做低秩近似（前 $k$ 个奇异值）+ 推导 PCA = $\\boldsymbol{X}$ 的右奇异向量\n"
        "- [ ] 至少做完 1 个 Sec 7 自由探索任务\n\n"
        "**Sec 8 轻量预告**——只需要「认识名字」，不需要懂细节\n\n"
        "- [ ] 知道 $L^2$ 范数后面在 Ch 7 会叫 **weight decay**\n"
        "- [ ] 能写出神经网络一层的公式 $\\boldsymbol{y} = \\boldsymbol{W}\\boldsymbol{x} + \\boldsymbol{b}$ + 形状传递\n"
        "- [ ] 知道大模型微调里 **LoRA** 的数学根基是 SVD 低秩近似\n"
        "- [ ] 给定 $(B, H, W, 3)$ 这样的 shape 元组，能讲出每维是什么意思\n"
    )
    b.code("checks.report()")


# =========================================================
# Build & save ch02 demo + work
# =========================================================

def build_ch02():
    b = Builder()
    ch02_header(b)
    ch02_sec0(b)
    ch02_sec1(b)
    ch02_sec2(b)
    ch02_sec3(b)
    ch02_sec4(b)
    ch02_sec5(b)
    ch02_sec6(b)
    ch02_sec7(b)
    ch02_sec8(b)
    ch02_checkpoint(b)
    write_ipynb(b.demo, "ch02-linear-algebra/ch02.ipynb")
    write_ipynb(b.work, "ch02-linear-algebra/ch02_work.ipynb")


def main():
    print("Building notebooks...")
    build_template()
    build_ch02()
    print("Done.")


if __name__ == "__main__":
    main()
