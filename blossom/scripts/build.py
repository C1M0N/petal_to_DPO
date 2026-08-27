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


# =========================================================
# Ch 3: 概率与信息论（结构按朱明超精读版花书 Ch 3 原文小节走）
# =========================================================
# 朱明超 Ch 3 三大块：
#   §1 概率（1.1 概率/随机变量 → 1.6 sigmoid/softplus）
#   §2 信息论（自信息 → KL/交叉熵）
#   §3 图模型（贝叶斯网 + 马尔可夫网）
# blossom 不再用 Sec 0-8 模板——函数按原文小节命名。
# 每节内部：📖 原文 → 直觉 → NumPy → 填空 → 必要可视化 → 后续预告（轻量）
# =========================================================


def ch03_header(b: Builder):
    b.md(
        "# 花书 · 第三章：概率与信息论\n\n"
        "> 你打开的是 demo / work 副本。**学习时用 work 副本**——\n"
        "> 教材副本只读（rebuild 时会被覆盖），做题请运行根目录的 `./start ch03`。\n\n"
        "## 配套资料\n\n"
        "- 📖 花书 PDF（vault）：`30 The Colonnade/36 Library/花书.pdf`\n"
        "- 📝 朱明超精读版：`花书拆解/重要章节/3 概率与信息论.pdf`\n"
        "- 🔧 Jupyter / NumPy 速查：忘了的话 [回 ch02 Sec 0](../ch02-linear-algebra/ch02.ipynb) 查\n"
        "- 🎯 用途：本章是 AI-303 Workshop **Day 1 M1（信息论 + KL）+ Day 1 M2（概率基础）+ Day 2 M4（概率深入）** 的直接弹药\n\n"
        "## 本章导航（按朱明超原文小节走，不再用 Sec 模板）\n\n"
        "| 节 | 主题 |\n"
        "|---|------|\n"
        "| §1.1 | 概率与随机变量（频率派 vs 贝叶斯派） |\n"
        "| §1.2 | 概率分布（PMF / PDF / CDF） |\n"
        "| §1.3 | 条件概率 + 条件独立 |\n"
        "| §1.4 | 期望 / 方差 / 协方差 |\n"
        "| §1.5 | 七大常用分布（Bernoulli / Multinoulli / Gaussian / 多元 Gaussian / Exponential / Laplace / Dirac） |\n"
        "| §1.6 | sigmoid + softplus |\n"
        "| **§2** | **信息论（自信息 / 熵 / 互信息 / KL / 交叉熵）— 本章重点** |\n"
        "| §3 | 图模型（贝叶斯网 + 马尔可夫网） |\n"
        "| CHECKPOINT | 章末自检清单 |\n\n"
        "## 学法\n\n"
        "1. 每节先看 📖 **花书原文**（朱明超精读版）的定义\n"
        "2. 跟着 blossom 的直觉解释 + 例题动手填 `___`\n"
        "3. 跑 cell 看 `checks.assert_*` 输出 ✅ / ❌\n"
        "4. **Workshop 钩子**：遇到「📍 Day X / 后续 Ch X」标记的句子，记一下名字就好——具体推导留到对应章节\n"
    )

    # 全章环境 + import（每个 cell 默认共享 kernel）
    b.code(
        "# 本章用到的所有库一次导入\n"
        "import sys\n"
        "sys.path.insert(0, '..')\n\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import scipy.stats\n"
        "from utils import checks, viz\n\n"
        "np.random.seed(0)  # 保证本章随机结果可复现"
    )


def ch03_p1_1_concept(b: Builder):
    b.md("---\n\n## §1.1 概率与随机变量\n")
    _yuanwen(
        b,
        "§1.1 概率与随机变量",
        "**频率学派概率 (Frequentist Probability)**：认为概率和事件发生的频率相关。\n\n"
        "**贝叶斯学派概率 (Bayesian Probability)**：认为概率是对某件事发生的确定程度，"
        "可以理解成是确信的程度。\n\n"
        "**随机变量 (Random Variable)**：一个可能随机取不同值的变量。"
        "例如：抛掷一枚硬币，出现正面或者反面的结果。"
    )
    b.md(
        "### 直觉：两个学派看同一件事\n\n"
        "**问题：抛一枚硬币正面朝上的概率是多少？**\n\n"
        "- **频率派**：扔 10000 次硬币，看正面出现的比例——如果 ≈ 0.5，那 $P(\\text{正}) = 0.5$。"
        "**概率是数出来的**。\n"
        "- **贝叶斯派**：在没扔之前，「正面朝上」这件事我多确定？综合「硬币看上去均匀」「制造工艺标准」等先验，"
        "我可以说 $P(\\text{正}) = 0.5$，这是我**对这件事的信念强度**。\n\n"
        "**两派的关键区别**：频率派认为「这枚特定硬币的下一次结果」**没有概率可言**"
        "（要么正要么反，谈不上 0.5）；而贝叶斯派可以谈「这一次的概率」——因为概率是我对世界的信念。\n\n"
        "**为什么这在深度学习里重要？**\n\n"
        "- 训练神经网络时，我们说「这张图片是猫的概率 = 0.87」——这是**贝叶斯派**的说法\n"
        "  （单张图片不能多次「重复」，但模型可以给出对它的信念强度）\n"
        "- 而我们衡量模型分类准确率「在 1000 张测试图上预测对了 86%」——这是**频率派**的视角\n\n"
        "📍 **Workshop 钩子**：贝叶斯思想在 Day 2 M6（MAP 估计）+ Day 3 M19（RLHF 的人类偏好）会反复出现——"
        "「奖励模型」可以看作对人类偏好的贝叶斯估计；KL 正则项的角色和贝叶斯先验等价。\n"
    )
    b.md(
        "### ✏️ 例题 1.1.E1：分辨学派\n\n"
        "下面 4 个陈述，分别属于频率派还是贝叶斯派？先在纸上写答案再展开下面 cell。\n\n"
        "| # | 陈述 |\n"
        "|---|------|\n"
        "| 1 | 这家医院过去十年新生儿男女比是 0.51 / 0.49 |\n"
        "| 2 | 综合家族病史 + 基因检测，张三未来 10 年得糖尿病的概率是 0.3 |\n"
        "| 3 | 这枚骰子摇 60 次，每个面大约出现 10 次，所以每面概率 1/6 |\n"
        "| 4 | 训练好的分类模型给一张测试图打分 0.92，所以它「应该」是猫 |\n"
    )
    b.code(
        "# 参考答案（判断标准：用「重复观察的比例」=频率派 / 用「主观信念 / 先验 / 单次事件」=贝叶斯派）\n"
        "answers = {\n"
        "    1: ('频率派', '数十年新生儿比例 = 重复观察出来的频率'),\n"
        "    2: ('贝叶斯派', '单个个体的未来事件 + 综合先验信息'),\n"
        "    3: ('频率派', '60 次试验的比例'),\n"
        "    4: ('贝叶斯派', '单张图片不能多次重复，模型输出 = 信念强度'),\n"
        "}\n"
        "for i, (school, why) in answers.items():\n"
        "    print(f'#{i}: {school}  —— {why}')"
    )


def ch03_p1_2_distribution(b: Builder):
    b.md("---\n\n## §1.2 概率分布（PMF / PDF / CDF）\n")

    # §1.2.1 PMF
    _yuanwen(
        b,
        "§1.2.1 概率质量函数 (PMF)",
        "**概率质量函数 (Probability Mass Function)**：对于离散型变量，"
        "我们先定义一个随机变量，然后用 $\\sim$ 符号来说明它遵循的分布："
        "$\\mathrm{x} \\sim P(\\mathrm{x})$，函数 $P$ 是随机变量 $\\mathrm{x}$ 的 PMF。\n\n"
        "例如，考虑一个离散型 $\\mathrm{x}$ 有 $k$ 个不同的值，"
        "我们可以假设 $\\mathrm{x}$ 是均匀分布的（也就是将它的每个值视为等可能的），"
        "通过将它的 PMF 设为：\n\n"
        "$$P(\\mathrm{x} = x_i) = \\frac{1}{k}$$\n\n"
        "对于所有的 $i$ 都成立。"
    )

    # §1.2.2 PDF
    _yuanwen(
        b,
        "§1.2.2 概率密度函数 (PDF)",
        "当研究的对象是连续型时，我们可以引入同样的概念。"
        "如果一个函数 $p$ 是**概率密度函数 (Probability Density Function)**：\n\n"
        "- 分布满足非负性条件：$\\forall x \\in \\mathrm{x},\\ p(x) \\geq 0$\n"
        "- 分布满足归一化条件：$\\int_{-\\infty}^{\\infty} p(x)\\,dx = 1$\n\n"
        "例如在 $(a, b)$ 上的均匀分布：\n\n"
        "$$U(x; a, b) = \\frac{\\mathbf{1}_{ab}(x)}{b - a}$$\n\n"
        "这里 $\\mathbf{1}_{ab}(x)$ 表示在 $(a, b)$ 内为 $1$，否则为 $0$。"
    )

    # §1.2.3 CDF
    _yuanwen(
        b,
        "§1.2.3 累积分布函数 (CDF)",
        "**累积分布函数 (Cummulative Distribution Function)** 表示对小于 $x$ 的概率的积分：\n\n"
        "$$\\mathrm{CDF}(x) = \\int_{-\\infty}^{x} p(t)\\,dt$$",
        "# 花书原文配套代码：均匀分布的 PDF + 1000 次采样直方图\n"
        "from scipy.stats import uniform\n"
        "fig, ax = plt.subplots(1, 1, figsize=(6, 3))\n"
        "r = uniform.rvs(loc=0, scale=1, size=1000)\n"
        "ax.hist(r, density=True, histtype='stepfilled', alpha=0.5, label='1000 次采样直方图')\n"
        "x = np.linspace(uniform.ppf(0.01), uniform.ppf(0.99), 100)\n"
        "ax.plot(x, uniform.pdf(x), 'r-', lw=3, alpha=0.8, label='uniform PDF (真值)')\n"
        "ax.legend(); ax.set_title('Uniform(0, 1) — 采样直方图 vs 解析 PDF')\n"
        "plt.show()"
    )

    b.md(
        "### 直觉：PMF vs PDF\n\n"
        "**关键区别**（很多人入门时被这一点卡住）：\n\n"
        "- **PMF 的输出就是概率**，所以 $P(\\mathrm{x}=x_i) \\in [0, 1]$\n"
        "- **PDF 的输出不是概率**——它是「单位长度的概率密度」，**可以 $> 1$**！\n"
        "  例如均匀分布 $U(0, 0.5)$ 在区间内 PDF $= 1/0.5 = 2$\n"
        "- **想拿到「真正的概率」必须积分**：$P(a \\le \\mathrm{x} \\le b) = \\int_a^b p(x)\\,dx$\n\n"
        "**为什么连续型变量「单点概率 = 0」？**\n\n"
        "对连续变量，$P(\\mathrm{x} = x_0) = \\int_{x_0}^{x_0} p(x)\\,dx = 0$——只有**区间**才有非零概率。"
        "记住：**PDF 像质量密度（kg/m³），不是质量本身**，要乘以体积（区间长度）才得到质量（概率）。\n"
    )

    b.md("### 可视化：把离散 vs 连续的 PMF/PDF/CDF 摆在一起\n")
    b.code(
        "from scipy.stats import bernoulli, norm\n"
        "fig, axes = plt.subplots(2, 2, figsize=(10, 6))\n\n"
        "# 离散：Bernoulli(0.3) 的 PMF + CDF\n"
        "p = 0.3\n"
        "axes[0, 0].bar([0, 1], bernoulli.pmf([0, 1], p), color='C0', width=0.4)\n"
        "axes[0, 0].set_title('PMF: Bernoulli(0.3)')\n"
        "axes[0, 0].set_xticks([0, 1]); axes[0, 0].set_ylim(0, 1)\n"
        "x_disc = np.linspace(-0.5, 1.5, 100)\n"
        "axes[0, 1].step(x_disc, bernoulli.cdf(x_disc, p), color='C0', where='post')\n"
        "axes[0, 1].set_title('CDF: Bernoulli(0.3) — 阶梯函数')\n\n"
        "# 连续：Normal(0, 1) 的 PDF + CDF\n"
        "x_cont = np.linspace(-3, 3, 200)\n"
        "axes[1, 0].plot(x_cont, norm.pdf(x_cont), color='C1', lw=2)\n"
        "axes[1, 0].fill_between(x_cont, norm.pdf(x_cont), alpha=0.3, color='C1')\n"
        "axes[1, 0].set_title('PDF: N(0, 1) — 光滑曲线')\n"
        "axes[1, 1].plot(x_cont, norm.cdf(x_cont), color='C1', lw=2)\n"
        "axes[1, 1].set_title('CDF: N(0, 1) — 单调递增 0→1')\n\n"
        "plt.tight_layout()\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 1.2.E1：PMF 归一化\n\n"
        "给定离散随机变量 $\\mathrm{x}$ 取值 $\\{1, 2, 3, 4\\}$，PMF 形式 $P(\\mathrm{x}=i) = c \\cdot i$。\n\n"
        "**任务**：找到归一化常数 $c$，让 $\\sum_i P(\\mathrm{x}=i) = 1$。\n\n"
        "**提示**：所有 PMF 值加起来必须 = 1。$c \\cdot (1+2+3+4) = 1$ 求 $c$。\n"
    )
    b.code(
        "values = np.array([1, 2, 3, 4])\n"
        "c = 1 / values.sum()                # 归一化常数 = 1 / 总和\n"
        "pmf = c * values\n"
        "print('c =', c)\n"
        "print('PMF =', pmf)\n"
        "print('sum =', pmf.sum())\n\n"
        "checks.assert_close('1.2.E1 归一化常数 c', c, 0.1)\n"
        "checks.assert_close('1.2.E1 PMF 总和=1', pmf.sum(), 1.0)",
        work_src=(
            "values = np.array([1, 2, 3, 4])\n"
            "c = ___                             # 用 1 / 总和 算\n"
            "pmf = c * values\n"
            "print('c =', c)\n"
            "print('PMF =', pmf)\n"
            "print('sum =', pmf.sum())\n\n"
            "checks.assert_close('1.2.E1 归一化常数 c', c, 0.1)\n"
            "checks.assert_close('1.2.E1 PMF 总和=1', pmf.sum(), 1.0)"
        )
    )

    b.md(
        "### ✏️ 例题 1.2.E2：用 CDF 算区间概率\n\n"
        "标准正态分布 $\\mathcal{N}(0, 1)$。**任务**：求 $P(-1 \\le \\mathrm{x} \\le 1)$"
        "（落在均值 $\\pm 1$ 个标准差以内的概率，应得到著名的「68%」）。\n\n"
        "**提示**：$P(a \\le \\mathrm{x} \\le b) = \\mathrm{CDF}(b) - \\mathrm{CDF}(a)$。"
        "`scipy.stats.norm.cdf(x)` 直接给标准正态的 CDF 值。\n"
    )
    b.code(
        "from scipy.stats import norm\n"
        "prob = norm.cdf(1) - norm.cdf(-1)\n"
        "print(f'P(-1 ≤ x ≤ 1) = {prob:.4f}')   # 应 ≈ 0.6827\n"
        "checks.assert_close('1.2.E2 正态 ±1σ', prob, 0.6827, tol=1e-3)",
        work_src=(
            "from scipy.stats import norm\n"
            "# 用 CDF 算区间概率：P(a ≤ x ≤ b) = CDF(b) - CDF(a)\n"
            "prob = ___\n"
            "print(f'P(-1 ≤ x ≤ 1) = {prob:.4f}')\n"
            "checks.assert_close('1.2.E2 正态 ±1σ', prob, 0.6827, tol=1e-3)"
        )
    )

    b.md(
        "### ✏️ 例题 1.2.E3：PDF 可以 > 1 的反直觉\n\n"
        "构造 $U(0, 0.2)$ 的 PDF，**先猜一猜**：PDF 输出会不会 $> 1$？\n\n"
        "**直觉**：PDF 是「密度」不是「概率」。区间 $[0, 0.2]$ 长度 0.2，"
        "总概率必须 = 1，所以 PDF $= 1 / 0.2 = 5$——大于 1 完全合法。\n"
    )
    b.code(
        "from scipy.stats import uniform\n"
        "X = uniform(loc=0, scale=0.2)        # U(0, 0.2)\n"
        "print('PDF 在 x=0.1 处:', X.pdf(0.1))                  # 5.0\n"
        "print('整个区间积分（区间概率）:', X.cdf(0.2) - X.cdf(0))  # 1.0\n\n"
        "checks.assert_close('1.2.E3 PDF 值=5', X.pdf(0.1), 5.0)\n"
        "checks.assert_close('1.2.E3 区间总概率=1', X.cdf(0.2) - X.cdf(0), 1.0)"
    )


def ch03_p1_3_conditional(b: Builder):
    b.md("---\n\n## §1.3 条件概率与条件独立\n")

    _yuanwen(
        b,
        "§1.3 边缘 / 条件 / 链式法则 / 独立 / 条件独立",
        "**边缘概率 (Marginal Probability)**：如果我们知道了一组变量的联合概率分布，"
        "但想要了解其中一个子集的概率分布。这种定义在子集上的概率分布被称为边缘概率分布：\n\n"
        "$$\\forall x \\in \\mathrm{x},\\ P(\\mathrm{x} = x) = \\sum_y P(\\mathrm{x} = x, \\mathrm{y} = y)$$\n\n"
        "**条件概率 (Conditional Probability)**：在很多情况下，我们感兴趣的是某个事件，"
        "在给定其他事件发生时出现的概率。这种概率叫做条件概率。"
        "我们将给定 $\\mathrm{x} = x$，$\\mathrm{y} = y$ 发生的条件概率记为 $P(\\mathrm{y}=y \\mid \\mathrm{x}=x)$，"
        "可以通过下面的公式计算：\n\n"
        "$$P(\\mathrm{y} = y \\mid \\mathrm{x} = x) = \\frac{P(\\mathrm{y} = y,\\, \\mathrm{x} = x)}{P(\\mathrm{x} = x)}$$\n\n"
        "**条件概率的链式法则 (Chain Rule of Conditional Probability)**：任何多维随机变量的联合概率分布，"
        "都可以分解成只有一个变量的条件概率相乘的形式：\n\n"
        "$$P(x_1, \\ldots, x_n) = P(x_1) \\prod_{i=2}^n P(x_i \\mid x_1, \\ldots, x_{i-1})$$\n\n"
        "**独立性 (Independence)**：两个随机变量 $\\mathrm{x}$ 和 $\\mathrm{y}$，"
        "如果它们的概率分布可以表示成两个因子的乘积形式，并且一个因子只包含 $\\mathrm{x}$ 另一个因子只包含 $\\mathrm{y}$，"
        "我们就称这两个随机变量是相互独立的：\n\n"
        "$$\\forall x \\in \\mathrm{x},\\ y \\in \\mathrm{y},\\ p(\\mathrm{x}=x, \\mathrm{y}=y) = p(\\mathrm{x}=x) p(\\mathrm{y}=y)$$\n\n"
        "**条件独立性 (Conditional Independence)**：如果关于 $\\mathrm{x}$ 和 $\\mathrm{y}$ 的条件概率分布对于 "
        "$\\mathrm{z}$ 的每一个值都可以写成乘积的形式，那么这两个随机变量 $\\mathrm{x}$ 和 $\\mathrm{y}$ "
        "在给定随机变量 $\\mathrm{z}$ 时是条件独立的：\n\n"
        "$$p(\\mathrm{x}=x, \\mathrm{y}=y \\mid \\mathrm{z}=z) = p(\\mathrm{x}=x \\mid \\mathrm{z}=z) p(\\mathrm{y}=y \\mid \\mathrm{z}=z)$$"
    )

    b.md(
        "### 直觉：从联合表格出发\n\n"
        "下面这张表是 1000 个学生的「主修学科 (x) × 是否选修 AI 课 (y)」联合分布表（人数）：\n\n"
        "|       | y=选 AI | y=不选 | **行总** |\n"
        "|-------|--------:|------:|-------:|\n"
        "| x=CS  |     320 |    80 |  **400** |\n"
        "| x=Math|     150 |   150 |  **300** |\n"
        "| x=Bio |      30 |   270 |  **300** |\n"
        "| **列总** | **500** | **500** | **1000** |\n\n"
        "**从这张表可以读出**：\n"
        "- **联合**：$P(\\mathrm{x}=\\text{CS}, \\mathrm{y}=\\text{选}) = 320/1000 = 0.32$\n"
        "- **边缘**（行/列加和）：$P(\\mathrm{x}=\\text{CS}) = 400/1000 = 0.4$\n"
        "- **条件**：$P(\\mathrm{y}=\\text{选} \\mid \\mathrm{x}=\\text{CS}) = 320/400 = 0.8$\n"
        "  「在 CS 学生里，80% 选了 AI」——这就是条件概率的直觉\n\n"
        "📍 **Workshop 钩子**：链式法则在 Day 4 写 nanoGPT 时直接用——\n"
        "  语言模型把整句话的概率分解成 $P(w_1, w_2, \\ldots, w_n) = \\prod_i P(w_i \\mid w_1, \\ldots, w_{i-1})$，"
        "  这就是「自回归生成」的数学根基。\n"
    )

    b.md(
        "### ✏️ 例题 1.3.E1：从联合表算边缘 + 条件\n\n"
        "用上面学科 × AI 课的表（联合 PMF 矩阵 `joint[i, j]` 表示行 i 列 j 的概率）。\n\n"
        "**任务**：\n"
        "1. 算 `P_x` ——边缘分布 $P(\\mathrm{x})$（按行求和）\n"
        "2. 算 `P_y_given_CS` —— 给定 $\\mathrm{x}=\\text{CS}$ 时 $\\mathrm{y}$ 的条件分布（应 = `[0.8, 0.2]`）\n\n"
        "**提示**：边缘 = `joint.sum(axis=1)`；条件 = 联合的某行 / 该行总和。\n"
    )
    b.code(
        "# 行 = CS / Math / Bio；列 = 选 AI / 不选\n"
        "joint = np.array([[0.32, 0.08],\n"
        "                  [0.15, 0.15],\n"
        "                  [0.03, 0.27]])\n"
        "assert np.isclose(joint.sum(), 1.0)\n\n"
        "P_x = joint.sum(axis=1)                       # 按行求和 → 边缘 P(x)\n"
        "P_y_given_CS = joint[0] / P_x[0]              # P(y | x=CS)\n\n"
        "print('P(x):              ', P_x)\n"
        "print('P(y | x=CS):       ', P_y_given_CS)\n\n"
        "checks.assert_close('1.3.E1 边缘 P(x)',     P_x, np.array([0.4, 0.3, 0.3]))\n"
        "checks.assert_close('1.3.E1 P(y|x=CS)',     P_y_given_CS, np.array([0.8, 0.2]))",
        work_src=(
            "joint = np.array([[0.32, 0.08],\n"
            "                  [0.15, 0.15],\n"
            "                  [0.03, 0.27]])\n"
            "assert np.isclose(joint.sum(), 1.0)\n\n"
            "P_x = ___                                     # 边缘 P(x)：joint 按行求和\n"
            "P_y_given_CS = ___                            # 条件 P(y | x=CS)：第 0 行 / P_x[0]\n\n"
            "print('P(x):              ', P_x)\n"
            "print('P(y | x=CS):       ', P_y_given_CS)\n\n"
            "checks.assert_close('1.3.E1 边缘 P(x)',     P_x, np.array([0.4, 0.3, 0.3]))\n"
            "checks.assert_close('1.3.E1 P(y|x=CS)',     P_y_given_CS, np.array([0.8, 0.2]))"
        )
    )

    b.md(
        "### ✏️ 例题 1.3.E2：链式法则验证\n\n"
        "对 3 个 0/1 随机变量 $x_1, x_2, x_3$，用链式法则：\n"
        "$$P(x_1, x_2, x_3) = P(x_1) \\cdot P(x_2 \\mid x_1) \\cdot P(x_3 \\mid x_1, x_2)$$\n\n"
        "**任务**：给定下面的边缘 / 条件分布，重建联合分布并验证总和 = 1。\n"
    )
    b.code(
        "# 假设：\n"
        "P_x1 = np.array([0.6, 0.4])                            # P(x1=0), P(x1=1)\n"
        "# P(x2 | x1)：行 = x1，列 = x2\n"
        "P_x2_given_x1 = np.array([[0.7, 0.3],\n"
        "                          [0.2, 0.8]])\n"
        "# P(x3 | x1, x2)：[x1][x2][x3]\n"
        "P_x3_given_x1x2 = np.array([[[0.9, 0.1], [0.5, 0.5]],\n"
        "                            [[0.4, 0.6], [0.1, 0.9]]])\n\n"
        "joint3 = np.zeros((2, 2, 2))\n"
        "for x1 in range(2):\n"
        "    for x2 in range(2):\n"
        "        for x3 in range(2):\n"
        "            joint3[x1, x2, x3] = (\n"
        "                P_x1[x1] * P_x2_given_x1[x1, x2] * P_x3_given_x1x2[x1, x2, x3]\n"
        "            )\n\n"
        "print('联合分布 shape:', joint3.shape)\n"
        "print('总和（必须=1）:', joint3.sum())\n"
        "checks.assert_close('1.3.E2 链式法则总和=1', joint3.sum(), 1.0)"
    )

    b.md(
        "### ✏️ 例题 1.3.E3：判断独立 vs 条件独立\n\n"
        "**独立的判别公式**：$\\mathrm{x} \\perp \\mathrm{y} \\iff P(x, y) = P(x) P(y)$ 对**所有** $(x, y)$ 成立。\n\n"
        "用上面 1.3.E1 的学科 × AI 表，判断 $\\mathrm{x}$（学科）和 $\\mathrm{y}$（是否选 AI）是否独立。\n"
    )
    b.code(
        "joint = np.array([[0.32, 0.08],\n"
        "                  [0.15, 0.15],\n"
        "                  [0.03, 0.27]])\n"
        "P_x = joint.sum(axis=1)                        # 边缘 P(x)\n"
        "P_y = joint.sum(axis=0)                        # 边缘 P(y)\n"
        "joint_if_indep = np.outer(P_x, P_y)            # P(x)P(y) 的乘积\n\n"
        "diff = np.abs(joint - joint_if_indep)\n"
        "print('联合分布:\\n', joint)\n"
        "print('独立假设下应为:\\n', np.round(joint_if_indep, 3))\n"
        "print('最大偏差:', diff.max())\n\n"
        "# 偏差远大于 0 → 不独立（CS 学生明显更倾向选 AI）\n"
        "is_indep = diff.max() < 0.01\n"
        "checks.assert_true('1.3.E3 学科与选 AI 不独立', not is_indep,\n"
        "                   hint=f'最大偏差 {diff.max():.3f} 远 > 0，说明分布有相关')"
    )


def ch03_p1_4_measures(b: Builder):
    b.md("---\n\n## §1.4 随机变量的度量（期望 / 方差 / 协方差）\n")

    _yuanwen(
        b,
        "§1.4 期望 / 方差 / 协方差",
        "**期望 (Expectation)**：函数 $f$ 关于概率分布 $P(\\mathrm{x})$ 或 $p(\\mathrm{x})$ 的期望"
        "表示为由概率分布产生 $x$，再计算 $f$ 作用到 $x$ 上后 $f(x)$ 的平均值。"
        "对于离散型随机变量，这可以通过求和得到：\n\n"
        "$$\\mathbb{E}_{\\mathrm{x} \\sim P}[f(x)] = \\sum_x P(x) f(x)$$\n\n"
        "对于连续型随机变量可以通过求积分得到：\n\n"
        "$$\\mathbb{E}_{\\mathrm{x} \\sim p}[f(x)] = \\int P(x) f(x)\\, dx$$\n\n"
        "另外，**期望是线性的**：\n\n"
        "$$\\mathbb{E}_{\\mathrm{x}}[\\alpha f(x) + \\beta g(x)] = \\alpha \\mathbb{E}_{\\mathrm{x}}[f(x)] + \\beta \\mathbb{E}_{\\mathrm{x}}[g(x)]$$\n\n"
        "**方差 (Variance)**：衡量的是当我们对 $x$ 依据它的概率分布进行采样时，"
        "随机变量 $\\mathrm{x}$ 的函数值会呈现多大的差异，描述采样得到的函数值在期望上下的波动程度：\n\n"
        "$$\\mathrm{Var}(f(x)) = \\mathbb{E}\\!\\left[(f(x) - \\mathbb{E}[f(x)])^2\\right]$$\n\n"
        "将方差开平方即为**标准差 (Standard Deviation)**。\n\n"
        "**协方差 (Covariance)**：用于衡量两组值之间的**线性相关程度**：\n\n"
        "$$\\mathrm{Cov}(f(x), g(y)) = \\mathbb{E}\\!\\left[(f(x) - \\mathbb{E}[f(x)])(g(y) - \\mathbb{E}[g(y)])\\right]$$\n\n"
        "**注意，独立比零协方差要求更强，因为独立还排除了非线性的相关。**",
        "# 花书原文配套代码：期望 / 方差 / 协方差\n"
        "x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])\n"
        "y = np.array([9, 8, 7, 6, 5, 4, 3, 2, 1])\n"
        "Mean = np.mean(x)\n"
        "Var = np.var(x)                # 默认总体方差（ddof=0）\n"
        "Var_unbias = np.var(x, ddof=1) # 样本方差（无偏估计）\n"
        "Cov = np.cov(x, y)\n"
        "print('Mean =', Mean)\n"
        "print('Var (总体) =', Var)\n"
        "print('Var (无偏) =', Var_unbias)\n"
        "print('Cov =\\n', Cov)"
    )

    b.md(
        "### 直觉：方差为什么有「总体」和「样本」两版？\n\n"
        "如果你**有全部数据**（整个总体），方差 = 平均「离差平方」，分母是 $N$：\n\n"
        "$$\\mathrm{Var}_{\\text{总体}} = \\frac{1}{N} \\sum_i (x_i - \\bar{x})^2$$\n\n"
        "但实践中我们一般**只有样本**，要估计未知的「总体方差」。统计学证明：\n"
        "上式会**系统性低估**总体方差（因为 $\\bar{x}$ 是用样本算的，已经「最小化」了离差平方）。\n"
        "正确做法是分母用 $N-1$（**Bessel 修正**）：\n\n"
        "$$\\mathrm{Var}_{\\text{样本}} = \\frac{1}{N-1} \\sum_i (x_i - \\bar{x})^2$$\n\n"
        "NumPy 用 `ddof` 参数控制：\n"
        "- `np.var(x)` = `np.var(x, ddof=0)` —— 总体方差（默认）\n"
        "- `np.var(x, ddof=1)` —— 样本方差（无偏估计，推荐）\n\n"
        "`np.cov(x, y)` 的**默认是 ddof=1**（和 var 默认相反！）。容易踩坑。\n"
    )

    b.md(
        "### 直觉：协方差 ≠ 独立\n\n"
        "- **零协方差** = 无**线性**相关\n"
        "- **独立** = 无**任何**形式的相关（线性 + 非线性）\n\n"
        "经典反例：$y = x^2$，$x$ 取 $\\{-1, -0.5, 0, 0.5, 1\\}$（对称分布）：\n"
        "- $\\mathbb{E}[x] = 0$，$\\mathbb{E}[xy] = \\mathbb{E}[x^3] = 0$ → 协方差 = 0\n"
        "- 但 $y$ 完全由 $x$ 决定 → **不独立**\n\n"
        "**这在深度学习里的体现**：神经网络层之间往往「协方差小但高度依赖」——"
        "因为依赖关系是高度非线性的，单看 Pearson 相关系数会漏掉。\n"
    )

    b.md(
        "### ✏️ 例题 1.4.E1：手写期望 vs np.mean\n\n"
        "给定离散分布 $P(\\mathrm{x}=1)=0.2, P(\\mathrm{x}=2)=0.5, P(\\mathrm{x}=3)=0.3$。\n\n"
        "**任务**：用定义 $\\mathbb{E}[\\mathrm{x}] = \\sum_x P(x) \\cdot x$ 手写算期望。\n\n"
        "**提示**：直接用向量点积 `(P * values).sum()` 或 `P @ values`。\n"
    )
    b.code(
        "values = np.array([1, 2, 3])\n"
        "P = np.array([0.2, 0.5, 0.3])\n"
        "assert np.isclose(P.sum(), 1.0)\n\n"
        "E = (P * values).sum()           # 期望 = Σ P(x) · x\n"
        "print('E[x] =', E)               # 0.2*1 + 0.5*2 + 0.3*3 = 2.1\n"
        "checks.assert_close('1.4.E1 期望', E, 2.1)",
        work_src=(
            "values = np.array([1, 2, 3])\n"
            "P = np.array([0.2, 0.5, 0.3])\n"
            "assert np.isclose(P.sum(), 1.0)\n\n"
            "E = ___                          # 用 Σ P(x) · x 手算（提示：(P * values).sum()）\n"
            "print('E[x] =', E)\n"
            "checks.assert_close('1.4.E1 期望', E, 2.1)"
        )
    )

    b.md(
        "### ✏️ 例题 1.4.E2：总体方差 vs 样本方差\n\n"
        "给一组样本 `data = [2, 4, 4, 4, 5, 5, 7, 9]`，分别用 `ddof=0` 和 `ddof=1` 算方差，"
        "并比较它们的差。\n\n"
        "**先猜**：`ddof=1` 算出来的应该比 `ddof=0` **大**还是**小**？（提示：分母从 N=8 变成 N-1=7）\n"
    )
    b.code(
        "data = np.array([2, 4, 4, 4, 5, 5, 7, 9], dtype=float)\n"
        "var_pop    = np.var(data, ddof=0)   # 总体方差，分母 N\n"
        "var_sample = np.var(data, ddof=1)   # 样本方差，分母 N-1\n"
        "print(f'总体方差 (ddof=0): {var_pop:.4f}')\n"
        "print(f'样本方差 (ddof=1): {var_sample:.4f}')\n"
        "print(f'比值: {var_sample / var_pop:.4f}（应 = N/(N-1) = 8/7 ≈ 1.143）')\n\n"
        "checks.assert_close('1.4.E2 总体方差', var_pop, 4.0)\n"
        "checks.assert_close('1.4.E2 样本方差', var_sample, 32/7, tol=1e-4)"
    )

    b.md(
        "### ✏️ 例题 1.4.E3：零协方差 ≠ 独立（反例）\n\n"
        "构造 $x = [-2, -1, 0, 1, 2]$，$y = x^2$。\n\n"
        "**先猜**：协方差 $\\mathrm{Cov}(x, y)$ 等于多少？\n\n"
        "**再算 + 理解**：$y$ 由 $x$ **完全决定**（看到 $x$ 就知道 $y$），但协方差却是 0。"
        "这就是「线性无关 ≠ 独立」的经典反例。\n"
    )
    b.code(
        "x = np.array([-2, -1, 0, 1, 2], dtype=float)\n"
        "y = x ** 2\n\n"
        "# np.cov 返回 2×2 矩阵：[[Var(x), Cov(x,y)], [Cov(x,y), Var(y)]]\n"
        "cov_mat = np.cov(x, y, ddof=0)\n"
        "print('协方差矩阵:\\n', cov_mat)\n"
        "print(f'Cov(x, y) = {cov_mat[0, 1]:.4f}')\n\n"
        "# 协方差≈0 但 y = x^2 完全由 x 决定 → 不独立\n"
        "checks.assert_close('1.4.E3 Cov(x, x²) = 0', cov_mat[0, 1], 0.0, tol=1e-10)"
    )


def ch03_p1_5_dists(b: Builder):
    b.md(
        "---\n\n## §1.5 常用概率分布\n\n"
        "本节按朱明超原文走 7 种分布。**学习目标**：看到分布名能立刻回忆出"
        "(1) 形状 (PDF/PMF 长什么样)、(2) 参数含义、(3) 在深度学习里典型出现场合。\n\n"
        "下面先定义一个**通用画图 helper** `plot_distribution(X, axes)`——"
        "复刻朱明超原文的 helper，给个 scipy.stats 分布对象就画它的 PMF/PDF + CDF。\n"
    )
    b.code(
        "# 通用分布画图 helper（inline 在本章用）\n"
        "def plot_distribution(X, axes=None, label_pdf='PDF', label_cdf='CDF'):\n"
        "    '''给定 scipy.stats 分布对象 X，画 PMF/PDF 和 CDF。'''\n"
        "    if axes is None:\n"
        "        fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n"
        "    x_min, x_max = X.interval(0.99)\n"
        "    x = np.linspace(x_min, x_max, 1000)\n"
        "    if hasattr(X.dist, 'pdf'):                # 连续型\n"
        "        axes[0].plot(x, X.pdf(x), label=label_pdf)\n"
        "        axes[0].fill_between(x, X.pdf(x), alpha=0.3)\n"
        "    else:                                     # 离散型\n"
        "        x_int = np.unique(x.astype(int))\n"
        "        axes[0].bar(x_int, X.pmf(x_int), label='PMF')\n"
        "    axes[1].plot(x, X.cdf(x), label=label_cdf)\n"
        "    for ax in axes:\n"
        "        ax.legend()\n"
        "        ax.grid(alpha=0.3)\n"
        "    return axes"
    )

    # §1.5.1 Bernoulli + Binomial
    _yuanwen(
        b,
        "§1.5.1 伯努利分布 (Bernoulli) + 二项分布",
        "**伯努利分布 (Bernoulli Distribution)** 是**单个二值随机变量**的分布，随机变量只有两种可能。"
        "它由一个参数 $\\phi \\in [0, 1]$ 控制，$\\phi$ 给出了随机变量等于 1 的概率：\n\n"
        "$$P(\\mathrm{x}=1) = \\phi,\\quad P(\\mathrm{x}=0) = 1 - \\phi,\\quad P(\\mathrm{x}=x) = \\phi^x (1 - \\phi)^{1-x}$$\n\n"
        "表示一次试验的结果要么成功要么失败。"
    )
    b.md(
        "📍 **Workshop 钩子**（轻量）：\n"
        "- 二分类神经网络输出经过 sigmoid 后就是一个 Bernoulli 参数 $\\phi$\n"
        "- Day 3 M18 InstructGPT 的 Bradley-Terry reward 模型："
        "  $P(y_w \\succ y_l) = \\sigma(r_w - r_l)$——这就是一个 Bernoulli\n"
    )
    b.code(
        "from scipy.stats import bernoulli\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n"
        "p = 0.3\n"
        "X = bernoulli(p)\n"
        "plot_distribution(X, axes=axes)\n"
        "fig.suptitle(f'Bernoulli(p={p})')\n"
        "plt.show()"
    )
    b.md("**Bernoulli 重复 n 次** → 二项分布 (Binomial)，统计「n 次试验里成功了几次」：")
    b.code(
        "# Bernoulli 一次 vs n 次 → 二项分布\n"
        "p = 0.3\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n\n"
        "# 一次试验（Bernoulli）\n"
        "n_samples = 1\n"
        "samples = np.random.binomial(n_samples, p, size=10000)\n"
        "axes[0].bar([0, 1], [(samples == 0).mean(), (samples == 1).mean()], label='Bernoulli')\n"
        "axes[0].set_title(f'Bernoulli({p}) - 1 次试验')\n"
        "axes[0].legend()\n\n"
        "# n=20 次试验（Binomial）\n"
        "n_samples = 20\n"
        "samples = np.random.binomial(n_samples, p, size=10000)\n"
        "x_int = np.arange(0, n_samples + 1)\n"
        "axes[1].bar(x_int, [(samples == k).mean() for k in x_int], label='Binomial')\n"
        "axes[1].set_title(f'Binomial(n={n_samples}, p={p}) - 20 次试验里成功 k 次的概率')\n"
        "axes[1].legend()\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 1.5.E1：Bernoulli 期望 + 方差\n\n"
        "对 $\\mathrm{x} \\sim \\mathrm{Bernoulli}(\\phi)$，理论上有 $\\mathbb{E}[\\mathrm{x}] = \\phi$ 和 "
        "$\\mathrm{Var}(\\mathrm{x}) = \\phi(1-\\phi)$。\n\n"
        "**任务**：用 10000 次采样验证这两个公式（$\\phi = 0.3$）。\n"
    )
    b.code(
        "phi = 0.3\n"
        "samples = np.random.binomial(1, phi, size=10000)\n"
        "mean_emp = samples.mean()\n"
        "var_emp = samples.var()\n"
        "print(f'采样均值 = {mean_emp:.4f}，理论 φ = {phi}')\n"
        "print(f'采样方差 = {var_emp:.4f}，理论 φ(1-φ) = {phi * (1-phi):.4f}')\n\n"
        "checks.assert_close('1.5.E1 Bernoulli 均值', mean_emp, phi, tol=0.02)\n"
        "checks.assert_close('1.5.E1 Bernoulli 方差', var_emp, phi * (1 - phi), tol=0.02)"
    )

    # §1.5.2 Multinoulli + Multinomial
    _yuanwen(
        b,
        "§1.5.2 范畴分布 (Multinoulli / Categorical) + 多项分布",
        "**范畴分布 (Multinoulli Distribution)** 是指在**具有 $k$ 个不同值**的单个离散型随机变量上的分布：\n\n"
        "$$p(\\mathrm{x} = x) = \\prod_i \\phi_i^{x_i}$$\n\n"
        "例如每次试验的结果就可以记为一个 $k$ 维的向量，只有此次试验的结果对应的维度记为 1，其他记为 0。"
    )
    b.md(
        "📍 **Workshop 钩子**（重点！）：\n"
        "- **语言模型的输出就是 Categorical 分布**：在词表的 $|V| \\approx 50000$ 个 token 上做选择\n"
        "- 神经网络最后一层 softmax 之后得到的就是 Categorical 分布的 $\\phi$\n"
        "- Day 2 M8 + Day 3 M21 nanoGPT 训练时，每个位置的 loss = $-\\log P(\\text{下一 token} \\mid \\text{前文})$，"
        "  这就是 Categorical 分布的负对数似然\n"
    )
    b.code(
        "# Categorical 一次 vs n 次 → 多项分布\n"
        "k = 5                                             # 5 个类别（比如骰子去掉一面）\n"
        "phi = np.array([0.1, 0.2, 0.3, 0.3, 0.1])         # 概率向量\n"
        "assert np.isclose(phi.sum(), 1.0)\n\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n\n"
        "# 一次试验：抽 1 个，每次只有 1 个 bin 为 1\n"
        "n_trials = 1\n"
        "sample = np.random.multinomial(n_trials, phi)\n"
        "axes[0].bar(range(k), sample, label=f'Multinoulli 1次 → {sample}')\n"
        "axes[0].set_title('Multinoulli 一次：只有 1 个 bin 为 1')\n"
        "axes[0].legend()\n\n"
        "# n=1000 次：成多项分布，估计真实 phi\n"
        "n_trials = 1000\n"
        "samples = np.random.multinomial(n_trials, phi)\n"
        "axes[1].bar(range(k), samples / n_trials, label='1000 次频率')\n"
        "axes[1].bar(range(k), phi, alpha=0.3, color='red', label='真值 φ')\n"
        "axes[1].set_title(f'Multinomial({n_trials} 次) 频率 vs 真值')\n"
        "axes[1].legend()\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 1.5.E2：softmax → Categorical 概率\n\n"
        "神经网络输出一组未归一化的「logits」$z$，要变成 Categorical 分布的概率向量，"
        "用 $\\mathrm{softmax}(z)_i = \\frac{e^{z_i}}{\\sum_j e^{z_j}}$。\n\n"
        "**任务**：给定 $z = [2.0, 1.0, 0.1, -1.0]$（4 类的 logits），算 softmax 后的概率。\n\n"
        "**数值稳定 trick**：先减去 $\\max(z)$ 再 exp（防止 $e^{z_i}$ 上溢）。\n"
    )
    b.code(
        "def softmax(z):\n"
        "    z = z - z.max()                  # 数值稳定：减最大值\n"
        "    e = np.exp(z)\n"
        "    return e / e.sum()\n\n"
        "z = np.array([2.0, 1.0, 0.1, -1.0])\n"
        "p = softmax(z)\n"
        "print('softmax(z) =', p)\n"
        "print('总和 =', p.sum())\n\n"
        "expected = np.array([0.6381, 0.2347, 0.0954, 0.0318])\n"
        "checks.assert_close('1.5.E2 softmax 概率', p, expected, tol=1e-3)\n"
        "checks.assert_close('1.5.E2 总和=1', p.sum(), 1.0)",
        work_src=(
            "def softmax(z):\n"
            "    # 提示：(1) 减 max 数值稳定 (2) np.exp (3) 除以和\n"
            "    z = z - z.max()\n"
            "    e = ___\n"
            "    return ___\n\n"
            "z = np.array([2.0, 1.0, 0.1, -1.0])\n"
            "p = softmax(z)\n"
            "print('softmax(z) =', p)\n"
            "print('总和 =', p.sum())\n\n"
            "expected = np.array([0.6381, 0.2347, 0.0954, 0.0318])\n"
            "checks.assert_close('1.5.E2 softmax 概率', p, expected, tol=1e-3)\n"
            "checks.assert_close('1.5.E2 总和=1', p.sum(), 1.0)"
        )
    )

    # §1.5.3 Gaussian
    _yuanwen(
        b,
        "§1.5.3 高斯分布 (Gaussian / Normal)",
        "**高斯分布 (Gaussian Distribution)** 或正态分布 (Normal Distribution) 形式如下：\n\n"
        "$$\\mathcal{N}(x; \\mu, \\sigma^2) = \\sqrt{\\frac{1}{2\\pi\\sigma^2}} "
        "\\exp\\!\\left(-\\frac{1}{2\\sigma^2}(x - \\mu)^2\\right)$$\n\n"
        "有时也会用 $\\beta = \\frac{1}{\\sigma^2}$ 表示分布的精度 (precision)。"
        "**中心极限定理 (Central Limit Theorem)** 认为，大量的独立随机变量的和近似于一个正态分布，"
        "因此可以认为噪声是属于正态分布的。"
    )
    b.md(
        "📍 **Workshop 钩子**：\n"
        "- NN 权重初始化普遍用 Gaussian（He / Xavier 初始化都基于 Gaussian 调方差）\n"
        "- Day 2 M9 Adam 优化器内部假设梯度分量近似 Gaussian\n"
        "- Day 5 Mini-DPO 训练时如果加入「探索噪声」也用 Gaussian\n"
    )
    b.code(
        "from scipy.stats import norm\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n"
        "mu, sigma = 0, 1\n"
        "X = norm(mu, sigma)         # 标准正态\n"
        "plot_distribution(X, axes=axes)\n"
        "fig.suptitle(f'N(μ={mu}, σ={sigma})')\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 1.5.E3：高斯分布的 68/95/99.7 法则\n\n"
        "对标准正态 $\\mathcal{N}(0, 1)$，「$\\mu \\pm k\\sigma$ 区间」的概率：\n"
        "- $k=1$ → ~68.3%\n"
        "- $k=2$ → ~95.4%\n"
        "- $k=3$ → ~99.7%\n\n"
        "**任务**：用 `norm.cdf` 验证这三个数值。\n"
    )
    b.code(
        "from scipy.stats import norm\n"
        "for k in [1, 2, 3]:\n"
        "    prob = norm.cdf(k) - norm.cdf(-k)\n"
        "    print(f'P(|x| ≤ {k}σ) = {prob:.4f}  →  {prob*100:.2f}%')\n\n"
        "checks.assert_close('1.5.E3 ±1σ', norm.cdf(1) - norm.cdf(-1), 0.6827, tol=1e-3)\n"
        "checks.assert_close('1.5.E3 ±2σ', norm.cdf(2) - norm.cdf(-2), 0.9545, tol=1e-3)\n"
        "checks.assert_close('1.5.E3 ±3σ', norm.cdf(3) - norm.cdf(-3), 0.9973, tol=1e-3)"
    )

    # §1.5.4 Multivariate Gaussian
    _yuanwen(
        b,
        "§1.5.4 多元高斯分布 (Multivariate Normal)",
        "多元正态分布 (Multivariate Normal Distribution) 形式如下：\n\n"
        "$$\\mathcal{N}(x; \\mu, \\Sigma) = \\sqrt{\\frac{1}{(2\\pi)^n \\det(\\Sigma)}} "
        "\\exp\\!\\left(-\\frac{1}{2}(x - \\mu)^\\top \\Sigma^{-1} (x - \\mu)\\right)$$\n\n"
        "其中 $\\mu \\in \\mathbb{R}^n$ 是均值向量，$\\Sigma \\in \\mathbb{R}^{n \\times n}$ 是协方差矩阵（正定）。"
    )
    b.md(
        "📍 **Workshop 钩子**：\n"
        "- VAE / 扩散模型的 latent space 假设多元 Gaussian\n"
        "- 协方差矩阵 $\\Sigma$ 的特征向量 = 数据的主成分（回 Ch 2 PCA 那条线）\n"
    )
    b.code(
        "# 朱明超原文配套：2D 多元正态的等高线\n"
        "from scipy.stats import multivariate_normal\n"
        "x, y = np.mgrid[-1:1:.01, -1:1:.01]\n"
        "pos = np.dstack((x, y))\n"
        "fig = plt.figure(figsize=(5, 5))\n"
        "ax = fig.add_subplot(111)\n"
        "mu = [0.5, -0.2]                  # 均值\n"
        "sigma = [[2.0, 0.3], [0.3, 0.5]]  # 协方差矩阵\n"
        "X = multivariate_normal(mu, sigma)\n"
        "cs = ax.contourf(x, y, X.pdf(pos), cmap='viridis')\n"
        "ax.scatter(*mu, c='red', s=50, label='μ', edgecolors='white')\n"
        "ax.set_title(f'2D Gaussian, μ={mu}, Σ={sigma}')\n"
        "ax.legend()\n"
        "plt.colorbar(cs)\n"
        "plt.show()"
    )

    # §1.5.5 Exponential
    _yuanwen(
        b,
        "§1.5.5 指数分布 (Exponential)",
        "指数分布 (Exponential Distribution) 形式如下：\n\n"
        "$$p(x; \\lambda) = \\lambda \\mathbf{1}_{x \\geq 0} \\exp(-\\lambda x)$$\n\n"
        "是用于在 $x = 0$ 处获得最高的概率的分布，其中 $\\lambda > 0$ 是分布的一个参数，"
        "常被称为率参数 (Rate Parameter)。"
    )
    b.code(
        "from scipy.stats import expon\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n"
        "X = expon(scale=1)                # scale = 1/λ\n"
        "plot_distribution(X, axes=axes)\n"
        "fig.suptitle('Exponential(λ=1)')\n"
        "plt.show()"
    )

    # §1.5.6 Laplace
    _yuanwen(
        b,
        "§1.5.6 拉普拉斯分布 (Laplace)",
        "拉普拉斯分布 (Laplace Distribution) 形式如下：\n\n"
        "$$\\mathrm{Laplace}(x; \\mu, \\gamma) = \\frac{1}{2\\gamma} \\exp\\!\\left(-\\frac{|x - \\mu|}{\\gamma}\\right)$$\n\n"
        "这也是可以在一个点获得比较高的概率的分布。"
    )
    b.md(
        "📍 **Workshop 钩子**：拉普拉斯分布的 NLL = $|x - \\mu|/\\gamma + \\text{常数}$——\n"
        "这就是 **L1 范数损失**的来源（相对的，Gaussian NLL = $L2$ 损失）。"
        "等到 Ch 7 讲正则化时会再相遇。\n"
    )
    b.code(
        "from scipy.stats import laplace\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n"
        "mu, gamma = 0, 1\n"
        "X = laplace(loc=mu, scale=gamma)\n"
        "plot_distribution(X, axes=axes)\n"
        "fig.suptitle(f'Laplace(μ={mu}, γ={gamma})')\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 1.5.E4：Laplace vs Gaussian 的「尾巴」\n\n"
        "Laplace 比 Gaussian 有**更厚的尾巴**（远离均值处概率更大）。\n"
        "**任务**：算「$|x| > 3$」在两种分布下的概率（都用 $\\mu=0, \\sigma=1$，Laplace 用 $\\gamma = 1/\\sqrt{2}$ 让方差相同）。\n"
    )
    b.code(
        "from scipy.stats import norm, laplace\n"
        "X_norm = norm(0, 1)\n"
        "X_lap = laplace(loc=0, scale=1/np.sqrt(2))   # 方差 = 2γ² = 1\n\n"
        "tail_norm = 2 * (1 - X_norm.cdf(3))           # P(|x| > 3) under Gaussian\n"
        "tail_lap  = 2 * (1 - X_lap.cdf(3))            # under Laplace\n"
        "print(f'Gaussian 尾巴概率: {tail_norm:.5f}')\n"
        "print(f'Laplace  尾巴概率: {tail_lap:.5f}')\n"
        "print(f'比值（Laplace 厚多少）: {tail_lap / tail_norm:.2f}x')\n\n"
        "checks.assert_true('1.5.E4 Laplace 尾巴更厚', tail_lap > tail_norm)"
    )

    # §1.5.7 Dirac
    _yuanwen(
        b,
        "§1.5.7 Dirac 分布 + 经验分布",
        "**Dirac delta 函数** 定义为 $p(x) = \\delta(x - \\mu)$，这是一个泛函数。"
        "它常被用于组成**经验分布 (Empirical Distribution)**：\n\n"
        "$$\\hat{p}(x) = \\frac{1}{m} \\sum_{i=1}^m \\delta(x - x^{(i)})$$"
    )
    b.md(
        "**直觉**：Dirac 函数把「全部概率压在一个点上」。经验分布就是把训练集每个数据点看成一个 Dirac，"
        "然后均匀分配概率——这就是「训练数据本身」的概率视角。\n\n"
        "📍 **Workshop 钩子**（重要！）：\n"
        "- Day 2 M5 推 **MLE = 最小化交叉熵**时，"
        "$\\hat{p}_{\\text{data}}$（真实数据分布）就用经验分布近似——一堆 Dirac 函数加起来\n"
        "- $\\theta_{\\mathrm{MLE}} = \\arg\\min_\\theta \\mathbb{E}_{x \\sim \\hat{p}_{\\text{data}}}\\!\\left[-\\log p_{\\text{model}}(x;\\theta)\\right]$ —— "
        "对经验分布求期望 = 对训练样本求平均\n"
    )
    b.code(
        "# 用直方图模拟「经验分布」（无法直接画 δ，但 1000 个样本的直方图就是它的可视化）\n"
        "samples = np.random.normal(0, 1, 50)               # 假装真实数据\n"
        "fig, ax = plt.subplots(figsize=(7, 3))\n"
        "ax.scatter(samples, np.zeros_like(samples), marker='|', s=200,\n"
        "           color='black', label=f'经验分布: 50 个 δ 函数')\n"
        "ax.axhline(0, color='gray', alpha=0.3)\n"
        "ax.set_title('经验分布 = 每个数据点一个 δ，权重 1/N')\n"
        "ax.set_yticks([])\n"
        "ax.legend()\n"
        "plt.show()"
    )


def ch03_p1_6_funcs(b: Builder):
    b.md("---\n\n## §1.6 常用函数：sigmoid + softplus\n")

    _yuanwen(
        b,
        "§1.6.1 logistic sigmoid 函数",
        "$$\\sigma(x) = \\frac{1}{1 + \\exp(-x)}$$\n\n"
        "logistic sigmoid 函数通常用来产生伯努利分布中的参数 $\\phi$，"
        "因为它的范围是 $(0, 1)$，处在 $\\phi$ 的有效取值范围内。"
        "sigmoid 函数在变量取绝对值非常大的正值或负值时会出现**饱和 (Saturate)** 现象，"
        "意味着函数会变得很平，并且对输入的微小改变会变得不敏感。"
    )

    _yuanwen(
        b,
        "§1.6.2 softplus 函数",
        "$$\\zeta(x) = \\log(1 + \\exp(x))$$\n\n"
        "softplus 函数可以用来产生正态分布的 $\\beta$ 和 $\\sigma$ 参数，因为它的范围是 $(0, \\infty)$。"
        "当处理包含 sigmoid 函数的表达式时它也经常出现。"
        "softplus 函数名来源于它是另外一个函数的平滑（或「软化」）形式，这个函数是：\n\n"
        "$$x^+ = \\max(0, x)$$",
        "# 花书原文配套代码：sigmoid + softplus 画图\n"
        "x = np.linspace(-10, 10, 100)\n"
        "sigmoid = 1 / (1 + np.exp(-x))\n"
        "softplus = np.log(1 + np.exp(x))\n"
        "fig, axes = plt.subplots(1, 2, figsize=(10, 3))\n"
        "axes[0].plot(x, sigmoid, label='sigmoid σ(x)')\n"
        "axes[0].axhline(0, color='gray', alpha=0.3)\n"
        "axes[0].axhline(1, color='gray', alpha=0.3, linestyle='--', label='饱和上限')\n"
        "axes[0].legend(); axes[0].set_title('sigmoid: (-∞, ∞) → (0, 1)')\n"
        "axes[1].plot(x, softplus, label='softplus ζ(x)')\n"
        "axes[1].plot(x, np.maximum(0, x), '--', alpha=0.5, label='max(0, x) = ReLU')\n"
        "axes[1].legend(); axes[1].set_title('softplus: (-∞, ∞) → (0, ∞)，是 ReLU 的「软化」')\n"
        "plt.show()"
    )

    b.md(
        "### 关键性质（记一下，后面会反复用）\n\n"
        "$$1 - \\sigma(x) = \\sigma(-x) \\qquad \\frac{d}{dx}\\sigma(x) = \\sigma(x)(1 - \\sigma(x))$$\n\n"
        "$$\\frac{d}{dx}\\zeta(x) = \\sigma(x) \\qquad \\zeta(x) - \\zeta(-x) = x$$\n\n"
        "**直觉**：sigmoid 把整条实数轴「挤压」进 $(0, 1)$——任何 logit / score 都能拿来做概率。"
    )

    b.md(
        "📍 **Workshop 钩子**（重要！）：\n\n"
        "**sigmoid 是 DPO 推导的起点之一**。Day 3 M18 InstructGPT 用 **Bradley-Terry 模型** "
        "训练 reward model：\n\n"
        "$$P(y_w \\succ y_l \\mid x) = \\sigma(r_\\phi(x, y_w) - r_\\phi(x, y_l))$$\n\n"
        "「在给定 prompt $x$ 下，输出 $y_w$ 比 $y_l$ 好」的概率 = "
        "**sigmoid 作用在两个 reward 之差上**。\n\n"
        "Day 4 M26 的 DPO loss 就是从这条公式 + KL 约束推出来的——\n"
        "**等你学到 Day 4 再回来看，这一节的 sigmoid 是核心零件**。\n"
    )

    b.md(
        "### ✏️ 例题 1.6.E1：验证 σ(-x) = 1 - σ(x)\n\n"
        "**任务**：手写 sigmoid，对 100 个随机 $x$ 验证 $\\sigma(-x) + \\sigma(x) = 1$。\n"
    )
    b.code(
        "def sigmoid(x):\n"
        "    return 1.0 / (1.0 + np.exp(-x))\n\n"
        "np.random.seed(0)\n"
        "x = np.random.randn(100) * 5      # 任意范围\n"
        "sum_pair = sigmoid(x) + sigmoid(-x)\n"
        "print(f'σ(x) + σ(-x) 最大偏差离 1: {np.abs(sum_pair - 1).max():.2e}')\n\n"
        "checks.assert_close('1.6.E1 σ(x)+σ(-x)=1', sum_pair, np.ones(100), tol=1e-10)",
        work_src=(
            "def sigmoid(x):\n"
            "    # 标准定义 σ(x) = 1 / (1 + exp(-x))\n"
            "    return ___\n\n"
            "np.random.seed(0)\n"
            "x = np.random.randn(100) * 5\n"
            "sum_pair = sigmoid(x) + sigmoid(-x)\n"
            "print(f'σ(x) + σ(-x) 最大偏差离 1: {np.abs(sum_pair - 1).max():.2e}')\n\n"
            "checks.assert_close('1.6.E1 σ(x)+σ(-x)=1', sum_pair, np.ones(100), tol=1e-10)"
        )
    )

    b.md(
        "### ✏️ 例题 1.6.E2：sigmoid 的数值稳定问题\n\n"
        "对很大的负 $x$（比如 $x = -1000$），$\\exp(-x) = \\exp(1000)$ 会**上溢**到 `inf`。\n\n"
        "**先猜**：naive 实现 `1 / (1 + np.exp(-x))` 在 $x = -1000$ 时会给出什么？\n"
        "**任务**：用 `np.where` 写一个数值稳定版本——$x \\geq 0$ 用原公式，$x < 0$ 用等价的 $e^x / (1 + e^x)$。\n"
    )
    b.code(
        "def sigmoid_stable(x):\n"
        "    return np.where(\n"
        "        x >= 0,\n"
        "        1.0 / (1.0 + np.exp(-x)),       # 大正数情况：分母不会爆\n"
        "        np.exp(x) / (1.0 + np.exp(x))   # 大负数情况：分子分母都很小\n"
        "    )\n\n"
        "import warnings\n"
        "with warnings.catch_warnings():\n"
        "    warnings.simplefilter('ignore')\n"
        "    # naive 在极端 x 会上溢\n"
        "    naive = 1.0 / (1.0 + np.exp(-np.array([-1000.0, 0.0, 1000.0])))\n"
        "stable = sigmoid_stable(np.array([-1000.0, 0.0, 1000.0]))\n"
        "print('naive  (x=-1000, 0, 1000):', naive)    # 可能 nan / overflow warning\n"
        "print('stable (x=-1000, 0, 1000):', stable)   # 干净的 [0, 0.5, 1]\n\n"
        "checks.assert_close('1.6.E2 stable @x=0', stable[1], 0.5)\n"
        "checks.assert_close('1.6.E2 stable @x=-1000', stable[0], 0.0)\n"
        "checks.assert_close('1.6.E2 stable @x=1000', stable[2], 1.0)"
    )

    b.md(
        "### ✏️ 例题 1.6.E3：softplus 是 sigmoid 的反导\n\n"
        "性质：$\\zeta'(x) = \\sigma(x)$。\n\n"
        "**任务**：用 `np.gradient` 数值求 softplus 的导数，和 sigmoid 直接计算的对比，验证它们近似相等。\n"
    )
    b.code(
        "x = np.linspace(-5, 5, 1000)\n"
        "softplus = np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)   # 数值稳定版\n"
        "dsoftplus_dx = np.gradient(softplus, x)                       # 数值梯度\n"
        "sigmoid_x = 1.0 / (1.0 + np.exp(-x))\n\n"
        "fig, ax = plt.subplots(figsize=(7, 3))\n"
        "ax.plot(x, dsoftplus_dx, label=\"数值微分: d/dx softplus\", lw=3)\n"
        "ax.plot(x, sigmoid_x, '--', label='σ(x) 直接计算', lw=2)\n"
        "ax.legend(); ax.set_title('验证: ζ\\'(x) = σ(x)')\n"
        "plt.show()\n\n"
        "max_err = np.abs(dsoftplus_dx - sigmoid_x).max()\n"
        "print(f'最大偏差: {max_err:.6f}')\n"
        "checks.assert_true('1.6.E3 ζ\\'(x) ≈ σ(x)', max_err < 0.01)"
    )


def ch03_p2_info_theory(b: Builder):
    b.md(
        "---\n\n# §2 信息论 — 本章重点\n\n"
        "这一节是 AI-303 Workshop **Day 1 M1** 直接弹药——\n"
        "KL 散度 + 交叉熵是后面 RLHF/DPO 推导的两块基石。学到这里能默写公式 = 后面省 10 倍力气。\n"
    )

    _yuanwen(
        b,
        "§2 信息论（自信息 / 熵 / 联合熵 / 条件熵 / 互信息）",
        "**信息论背后的思想：一件不太可能的事件比一件比较可能的事件更有信息量。**\n\n"
        "信息 (Information) 需要满足的三个条件：\n\n"
        "- 比较可能发生的事件的信息量要少。\n"
        "- 比较不可能发生的事件的信息量要大。\n"
        "- 独立发生的事件之间的信息量应该是可以叠加的。"
        "例如，投掷的硬币两次正面朝上传递的信息量，应该是投掷一次硬币正面朝上的信息量的两倍。\n\n"
        "**自信息 (Self-Information)**：对事件 $\\mathrm{x} = x$，我们定义：\n\n"
        "$$I(x) = -\\log P(x)$$\n\n"
        "自信息满足上面三个条件，单位是奈特 (nats)（底为 $e$）。\n\n"
        "**香农熵 (Shannon Entropy)**：上述的自信息只包含一个事件的信息，"
        "而**对于整个概率分布 $P$**，不确定性可以这样衡量：\n\n"
        "$$\\mathbb{E}_{x \\sim P}[I(x)] = -\\mathbb{E}_{x \\sim P}[\\log P(x)]$$\n\n"
        "也可以表示成 $H(P)$。香农熵是编码原理中最优编码长度。\n\n"
        "**多个随机变量**：\n\n"
        "- **联合熵 (Joint Entropy)**：表示同时考虑多个事件的条件下（即考虑联合分布概率）的熵。\n\n"
        "$$H(X, Y) = -\\sum_{x, y} P(x, y) \\log(P(x, y))$$\n\n"
        "- **条件熵 (Conditional Entropy)**：表示某件事情已经发生的情况下，另外一件事情的熵。\n\n"
        "$$H(X \\mid Y) = -\\sum_y P(y) \\sum_x P(x \\mid y) \\log(P(x \\mid y))$$\n\n"
        "- **互信息 (Mutual Information)**：表示两个事件的信息**相交**的部分。\n\n"
        "$$I(X, Y) = H(X) + H(Y) - H(X, Y)$$\n\n"
        "- **信息变差 (Variation of Information)**：表示两个事件的信息**不相交**的部分。\n\n"
        "$$V(X, Y) = H(X, Y) - I(X, Y)$$"
    )

    b.md(
        "### 直觉：为什么 $-\\log P$？\n\n"
        "你想要一个「信息量」函数 $I(x)$ 满足上面三个条件。**独立事件叠加**那条最关键："
        "$P(x, y) = P(x) P(y) \\Rightarrow I(x, y) = I(x) + I(y)$。\n\n"
        "什么函数能把「乘法」变成「加法」？$\\log$。\n\n"
        "再要求「越罕见信息量越大」（小概率 → 大信息），所以加负号 → $I(x) = -\\log P(x)$。"
        "唯一选择，没有任何 ad-hoc。\n\n"
        "**单位**：以 $e$ 为底叫 **nats**（自然单位，深度学习里用），以 2 为底叫 **bits**（通信学里用）。\n"
    )

    b.md("### 可视化：二值分布的熵 $H(p)$ —— 朱明超原文图 7")
    b.code(
        "# 复刻朱明超原文图：H(p) = -p log p - (1-p) log(1-p)\n"
        "p = np.linspace(1e-6, 1 - 1e-6, 100)\n"
        "entropy = -p * np.log(p) - (1 - p) * np.log(1 - p)\n"
        "plt.figure(figsize=(5, 4))\n"
        "plt.plot(p, entropy)\n"
        "plt.axvline(0.5, color='red', linestyle='--', alpha=0.5, label='p=0.5 → 最大熵 ln 2 ≈ 0.693')\n"
        "plt.xlabel('p (Bernoulli 参数)')\n"
        "plt.ylabel('Shannon entropy H(p) [nats]')\n"
        "plt.title('二值分布的熵: 最不确定 = 50/50')\n"
        "plt.legend()\n"
        "plt.grid(alpha=0.3)\n"
        "plt.show()"
    )
    b.md(
        "**看图直觉**：\n"
        "- $p = 0$ 或 $p = 1$ → 熵 = 0（完全确定，没有信息）\n"
        "- $p = 0.5$ → 熵最大 $= \\ln 2 \\approx 0.693$ nats（最不确定）\n"
        "- **熵 = 描述这个分布所需的「最少平均比特数」**"
    )

    b.md(
        "### ✏️ 例题 2.E1：手写自信息 + 验证罕见性\n\n"
        "**任务**：算下面 4 个事件的自信息（nats），验证「越罕见信息量越大」。\n\n"
        "| 事件 | 概率 |\n|------|------|\n"
        "| 太阳明天升起 | 0.9999999 |\n| 抛硬币正面 | 0.5 |\n"
        "| 你今天买彩票中头奖 | 1e-7 |\n| 不可能事件（占位） | 1e-12 |\n"
    )
    b.code(
        "def self_info(p):\n"
        "    return -np.log(p)\n\n"
        "events = [('太阳明天升起', 0.9999999),\n"
        "          ('抛硬币正面', 0.5),\n"
        "          ('彩票头奖', 1e-7),\n"
        "          ('几乎不可能', 1e-12)]\n"
        "for name, p in events:\n"
        "    print(f'{name:<15s} p={p:<12.1e}  I(x) = {self_info(p):.3f} nats')\n\n"
        "# 越罕见，I 越大\n"
        "checks.assert_true('2.E1 罕见事件 I 更大', self_info(1e-7) > self_info(0.5))",
        work_src=(
            "def self_info(p):\n"
            "    # 自信息 I(x) = -log P(x)\n"
            "    return ___\n\n"
            "events = [('太阳明天升起', 0.9999999),\n"
            "          ('抛硬币正面', 0.5),\n"
            "          ('彩票头奖', 1e-7),\n"
            "          ('几乎不可能', 1e-12)]\n"
            "for name, p in events:\n"
            "    print(f'{name:<15s} p={p:<12.1e}  I(x) = {self_info(p):.3f} nats')\n\n"
            "checks.assert_true('2.E1 罕见事件 I 更大', self_info(1e-7) > self_info(0.5))"
        )
    )

    b.md(
        "### ✏️ 例题 2.E2：手写香农熵 + scipy 对比\n\n"
        "**任务**：手写 $H(P) = -\\sum_i P_i \\log P_i$，对几个分布算熵，"
        "并用 `scipy.stats.entropy` 验证。\n\n"
        "**提示**：注意 $P_i = 0$ 时 $0 \\log 0 \\to 0$（约定，避免 NaN），用 `np.where` 处理。\n"
    )
    b.code(
        "def shannon_entropy(P):\n"
        "    P = np.asarray(P, dtype=float)\n"
        "    return -np.sum(np.where(P > 0, P * np.log(P), 0.0))\n\n"
        "from scipy.stats import entropy\n"
        "for name, P in [\n"
        "    ('均匀 [0.25]*4', [0.25, 0.25, 0.25, 0.25]),\n"
        "    ('偏分布 [0.7,0.2,0.1]', [0.7, 0.2, 0.1]),\n"
        "    ('确定 [1,0,0]', [1.0, 0.0, 0.0]),\n"
        "]:\n"
        "    h_mine = shannon_entropy(P)\n"
        "    h_scipy = entropy(P)\n"
        "    print(f'{name:<25s} 手写={h_mine:.4f}  scipy={h_scipy:.4f}')\n"
        "    checks.assert_close(f'2.E2 H({name})', h_mine, h_scipy)",
        work_src=(
            "def shannon_entropy(P):\n"
            "    P = np.asarray(P, dtype=float)\n"
            "    # 实现 H(P) = -Σ P_i log P_i，注意 P_i=0 时贡献 = 0\n"
            "    return ___\n\n"
            "from scipy.stats import entropy\n"
            "for name, P in [\n"
            "    ('均匀 [0.25]*4', [0.25, 0.25, 0.25, 0.25]),\n"
            "    ('偏分布 [0.7,0.2,0.1]', [0.7, 0.2, 0.1]),\n"
            "    ('确定 [1,0,0]', [1.0, 0.0, 0.0]),\n"
            "]:\n"
            "    h_mine = shannon_entropy(P)\n"
            "    h_scipy = entropy(P)\n"
            "    print(f'{name:<25s} 手写={h_mine:.4f}  scipy={h_scipy:.4f}')\n"
            "    checks.assert_close(f'2.E2 H({name})', h_mine, h_scipy)"
        )
    )

    # ===== KL 散度 + 交叉熵 (核心) =====
    _yuanwen(
        b,
        "§2 KL 散度 + 交叉熵",
        "**KL 散度 (Kullback-Leibler Divergence)** 用于衡量两个分布 $P(\\mathrm{x})$ 和 $Q(\\mathrm{x})$ 之间的差距：\n\n"
        "$$D_{\\mathrm{KL}}(P \\| Q) = \\mathbb{E}_{x \\sim P}\\!\\left[\\log \\frac{P(x)}{Q(x)}\\right] "
        "= \\mathbb{E}_{x \\sim P}\\!\\left[\\log P(x) - \\log Q(x)\\right]$$\n\n"
        "注意 $D_{\\mathrm{KL}}(P\\|Q) \\neq D_{\\mathrm{KL}}(Q\\|P)$，**不满足对称性**。\n\n"
        "**交叉熵 (Cross Entropy)**：\n\n"
        "$$H(P, Q) = H(P) + D_{\\mathrm{KL}}(P \\| Q) = -\\mathbb{E}_{x \\sim P}[\\log Q(x)]$$\n\n"
        "假设 $P$ 是真实分布，$Q$ 是模型分布，那么**最小化交叉熵 $H(P, Q)$ 可以让模型分布逼近真实分布**。"
    )

    b.md(
        "### 直觉：KL 散度的两个视角\n\n"
        "**视角 1**（编码视角）：KL 是「用 $Q$ 的最优编码去编码来自 $P$ 的样本，比用 $P$ 自己的最优编码多用多少比特」。"
        "$Q$ 越像 $P$，多用的比特越少；$Q$ 完全等于 $P$ → KL = 0。\n\n"
        "**视角 2**（似然比期望）：KL = $\\mathbb{E}_P\\!\\left[\\log\\frac{P}{Q}\\right]$ —— 在真实分布 $P$ 下，"
        "「真实概率 / 模型概率」的对数比的平均值。$Q$ 在 $P$ 高概率处给的概率越小，KL 越大。\n\n"
        "**关键性质**：\n"
        "- $D_{\\mathrm{KL}}(P\\|Q) \\geq 0$，等号当且仅当 $P = Q$（Gibbs' inequality）\n"
        "- **不对称**：$D_{\\mathrm{KL}}(P\\|Q) \\neq D_{\\mathrm{KL}}(Q\\|P)$ —— 这意味着「用 $Q$ 拟合 $P$」和「用 $P$ 拟合 $Q$」**目标不同**\n"
    )

    b.md(
        "### 📍 Workshop 钩子（**必读**，本章最重要的两条桥接）\n\n"
        "1. **RLHF 的 KL penalty**（Day 3 M18 InstructGPT）：\n"
        "$$\\max_{\\pi_\\theta} \\mathbb{E}_{x, y \\sim \\pi_\\theta}[r_\\phi(x, y)] - \\beta\\, D_{\\mathrm{KL}}[\\pi_\\theta \\| \\pi_{\\text{ref}}]$$\n"
        "「让奖励高，但别离参考策略太远」——KL 是「弹簧」，$\\beta$ 是弹性系数。这条公式没 KL 散度就不存在。\n\n"
        "2. **MLE = 最小化交叉熵**（Day 2 M5 推导核心）：\n"
        "$$\\theta_{\\mathrm{MLE}} = \\arg\\min_\\theta H(\\hat{p}_{\\text{data}}, p_{\\text{model}}) "
        "= \\arg\\min_\\theta \\mathbb{E}_{x \\sim \\hat{p}_{\\text{data}}}\\!\\left[-\\log p_{\\text{model}}(x; \\theta)\\right]$$\n"
        "训练任何一个神经网络分类器/语言模型，loss = 交叉熵 = MLE 等价。Day 4 写 nanoGPT 训练循环，loss 函数就是它。\n\n"
        "3. **DPO 推导依赖正向 vs 反向 KL 不对称**（Day 4 M26）：知道这个区别能让你后面读 DPO 论文更轻松。"
    )

    b.md(
        "### ✏️ 例题 2.E3：手写 KL 散度 + scipy 对比\n\n"
        "**任务**：实现 $D_{\\mathrm{KL}}(P\\|Q) = \\sum_i P_i \\log \\frac{P_i}{Q_i}$，并和 `scipy.stats.entropy(P, Q)` 对比"
        "（scipy 的 `entropy(P, Q)` 就是 $D_{\\mathrm{KL}}(P\\|Q)$）。\n\n"
        "**约定**：$P_i = 0$ 时该项贡献 = 0。\n"
    )
    b.code(
        "def kl_divergence(P, Q):\n"
        "    P = np.asarray(P, dtype=float)\n"
        "    Q = np.asarray(Q, dtype=float)\n"
        "    return np.sum(np.where(P > 0, P * np.log(P / Q), 0.0))\n\n"
        "from scipy.stats import entropy\n"
        "P = np.array([0.1, 0.4, 0.5])\n"
        "Q = np.array([0.2, 0.3, 0.5])\n\n"
        "kl_mine = kl_divergence(P, Q)\n"
        "kl_scipy = entropy(P, Q)\n"
        "print(f'D_KL(P || Q) = {kl_mine:.6f}（scipy: {kl_scipy:.6f}）')\n"
        "checks.assert_close('2.E3 KL 散度', kl_mine, kl_scipy)\n"
        "# 自己等自己 → KL = 0\n"
        "checks.assert_close('2.E3 KL(P||P)=0', kl_divergence(P, P), 0.0)",
        work_src=(
            "def kl_divergence(P, Q):\n"
            "    P = np.asarray(P, dtype=float)\n"
            "    Q = np.asarray(Q, dtype=float)\n"
            "    # 实现 Σ P_i · log(P_i / Q_i)，P_i=0 时贡献 = 0\n"
            "    return ___\n\n"
            "from scipy.stats import entropy\n"
            "P = np.array([0.1, 0.4, 0.5])\n"
            "Q = np.array([0.2, 0.3, 0.5])\n\n"
            "kl_mine = kl_divergence(P, Q)\n"
            "kl_scipy = entropy(P, Q)\n"
            "print(f'D_KL(P || Q) = {kl_mine:.6f}（scipy: {kl_scipy:.6f}）')\n"
            "checks.assert_close('2.E3 KL 散度', kl_mine, kl_scipy)\n"
            "checks.assert_close('2.E3 KL(P||P)=0', kl_divergence(P, P), 0.0)"
        )
    )

    b.md(
        "### ✏️ 例题 2.E4：验证 $H(P, Q) = H(P) + D_{\\mathrm{KL}}(P\\|Q)$\n\n"
        "**任务**：分别算交叉熵 $H(P, Q) = -\\sum P_i \\log Q_i$、香农熵 $H(P)$、KL $D_{\\mathrm{KL}}(P\\|Q)$，"
        "验证恒等式 $H(P, Q) = H(P) + D_{\\mathrm{KL}}(P\\|Q)$。\n"
    )
    b.code(
        "def cross_entropy(P, Q):\n"
        "    P = np.asarray(P, dtype=float)\n"
        "    Q = np.asarray(Q, dtype=float)\n"
        "    return -np.sum(np.where(P > 0, P * np.log(Q), 0.0))\n\n"
        "P = np.array([0.1, 0.4, 0.5])\n"
        "Q = np.array([0.2, 0.3, 0.5])\n\n"
        "H_P = shannon_entropy(P)\n"
        "H_PQ = cross_entropy(P, Q)\n"
        "KL = kl_divergence(P, Q)\n"
        "print(f'H(P) = {H_P:.6f}')\n"
        "print(f'D_KL(P||Q) = {KL:.6f}')\n"
        "print(f'H(P,Q) = {H_PQ:.6f}（应 = H(P) + KL = {H_P + KL:.6f}）')\n\n"
        "checks.assert_close('2.E4 H(P,Q)=H(P)+KL', H_PQ, H_P + KL)"
    )

    b.md(
        "### ✏️ 例题 2.E5：KL 不对称——朱明超原文图 9 复刻（重要！）\n\n"
        "**场景**：真实分布 $P$ 是双峰高斯混合（如 $\\mathcal{N}(3, 0.5) + \\mathcal{N}(6, 0.5)$）。\n"
        "用**单峰**高斯 $Q$ 去拟合，分别最小化两种 KL：\n\n"
        "- **正向 KL** $\\arg\\min_q D_{\\mathrm{KL}}(P\\|Q)$ → $Q$ 倾向**覆盖** $P$ 的所有峰（mean-seeking）\n"
        "- **反向 KL** $\\arg\\min_q D_{\\mathrm{KL}}(Q\\|P)$ → $Q$ 倾向**挑一个峰**（mode-seeking）\n\n"
        "**这就是 DPO 推导里反复出现的「KL 不对称」现象的根源**。\n"
    )
    b.code(
        "from scipy.stats import norm, entropy\n"
        "from scipy.integrate import trapezoid    # NumPy 2.0+ 移走了 np.trapz，用 scipy 更稳\n\n"
        "# 真实双峰分布 p(x)\n"
        "x = np.linspace(1, 8, 500)\n"
        "p = norm.pdf(x, 3, 0.5) + norm.pdf(x, 6, 0.5)\n"
        "p = p / trapezoid(p, x)             # 归一化\n\n"
        "# 在所有 (μ, σ) 网格上找正向 / 反向 KL 最小的 q\n"
        "KL_pq, KL_qp, q_list = [], [], []\n"
        "for mu in np.linspace(0, 10, 50):\n"
        "    for sigma in np.linspace(0.1, 5, 50):\n"
        "        q = norm.pdf(x, mu, sigma)\n"
        "        q = q / trapezoid(q, x)      # 归一化\n"
        "        q_list.append(q)\n"
        "        KL_pq.append(trapezoid(np.where(p > 0, p * np.log(p / (q + 1e-12)), 0), x))\n"
        "        KL_qp.append(trapezoid(np.where(q > 0, q * np.log(q / (p + 1e-12)), 0), x))\n"
        "q_pq_min = q_list[int(np.argmin(KL_pq))]\n"
        "q_qp_min = q_list[int(np.argmin(KL_qp))]\n\n"
        "fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))\n"
        "axes[0].plot(x, p, 'b', label='p(x) 真实双峰', lw=2)\n"
        "axes[0].plot(x, q_pq_min, 'g--', label='q*(x)', lw=2)\n"
        "axes[0].set_title('正向 KL：q* = argmin D_KL(p||q) → 覆盖型')\n"
        "axes[0].legend()\n"
        "axes[1].plot(x, p, 'b', label='p(x) 真实双峰', lw=2)\n"
        "axes[1].plot(x, q_qp_min, 'g--', label='q*(x)', lw=2)\n"
        "axes[1].set_title('反向 KL：q* = argmin D_KL(q||p) → 挑峰型')\n"
        "axes[1].legend()\n"
        "plt.suptitle('KL 散度的不对称性：决定了 q 的拟合策略')\n"
        "plt.show()\n"
        "print('→ 正向 KL 选了「胖单峰」覆盖两个真峰（mean-seeking / 0-avoiding）')\n"
        "print('→ 反向 KL 选了「瘦单峰」挑一个真峰（mode-seeking / 0-forcing）')"
    )

    b.md(
        "### ✏️ 例题 2.E6：演示「最优编码 = 熵」（朱明超原文示例）\n\n"
        "对一段 ASCII 文本，逐字符算频率，再算 $H = -\\sum p_i \\log_2 p_i$（**底为 2** → 单位 bits）。\n"
        "这就是这段文本用最优编码每字符**至少**需要的比特数。\n\n"
        "**任务**：复刻朱明超原文 H 函数，对随机文本验证 H ≈ log₂(可能字符数)。\n"
    )
    b.code(
        "import math, random\n\n"
        "def H_bits(sentence):\n"
        "    entropy = 0.0\n"
        "    for c in range(256):\n"
        "        Px = sentence.count(chr(c)) / len(sentence)\n"
        "        if Px > 0:\n"
        "            entropy += -Px * math.log(Px, 2)   # 底 2 → bits\n"
        "    return entropy\n\n"
        "# 用 64 个不同字符随机生成长文本——理论熵应 ≈ log2(64) = 6 bits/char\n"
        "random.seed(42)\n"
        "simple_message = ''.join([chr(random.randint(0, 64)) for _ in range(5000)])\n"
        "h = H_bits(simple_message)\n"
        "print(f'实测熵 H = {h:.4f} bits/char（理论上限 log2(65) ≈ {math.log(65, 2):.4f}）')\n"
        "checks.assert_true('2.E6 H 接近 log2(N)', abs(h - math.log(65, 2)) < 0.3)"
    )


def ch03_p3_graphical(b: Builder):
    b.md(
        "---\n\n## §3 图模型 (Graphical Models)\n\n"
        "**警告**：本节是「先打照面」级别——花书 Ch 16 才完整讲图模型。"
        "现在的目标只是知道**贝叶斯网 / 马尔可夫网长什么样、为什么需要它们**，"
        "以及**因子分解**这个核心思想（直接通向 Day 4 nanoGPT 的自回归概率分解）。\n"
    )

    _yuanwen(
        b,
        "§3 图模型引入",
        "机器学习算法会涉及到非常多的随机变量上的概率分布。"
        "利用分解可以减少表示联合分布的成本，"
        "于是用图来表示概率分布的分解，这称为**结构化概率模型 (Structured Probabilistic Model)** "
        "或者**图模型 (Graphical Model)**。"
    )

    b.md(
        "### 为什么需要图模型？\n\n"
        "假设你有 30 个二值随机变量。要写出完整的联合分布 $P(x_1, \\ldots, x_{30})$，"
        "需要 $2^{30} \\approx 10^9$ 个参数。**完全无法处理**。\n\n"
        "但**很多变量之间没有直接依赖关系**。利用条件独立性，可以把联合分布**分解**成局部因子的乘积，"
        "参数量从指数级降到线性级。**图就是这种条件独立结构的画法**。\n"
    )

    # §3.1 有向图模型
    _yuanwen(
        b,
        "§3.1 有向图模型 (Directed Model) — 贝叶斯网",
        "有向图模型的概率可以因子分解 $P(x) = P(x_1, \\ldots, x_i, \\ldots) = \\prod_i P(x_i \\mid \\mathrm{PA}(x_i))$，"
        "其中 $\\mathrm{PA}(x_i)$ 是 $x_i$ 的父节点，单个因子 $P(x_i \\mid \\mathrm{PA}(x_i))$ 称为**条件概率分布 (CPD)**。"
        "示例如下图所示，有：\n\n"
        "$$P(a, b, c, d, e) = P(a) P(b \\mid a) P(c \\mid a, b) P(d \\mid b) P(e \\mid c)$$\n\n"
        "（图 1：贝叶斯网示例，节点 a→b, a→c, b→c, b→d, c→e）\n\n"
        "**有向图的代表是贝叶斯网。**\n\n"
        "贝叶斯网与朴素贝叶斯模型建立在相同的直观假设上：**通过利用分布的条件独立性来获得紧凑而自然的表示。**"
        "贝叶斯网核心是一个**有向无环图 (DAG)**，"
        "其节点为论域中的随机变量，节点间的有向箭头表示这两个节点的依赖关系。\n\n"
        "贝叶斯网可以看作是**各特征节点间的依赖关系图**（有向无环图表示）"
        "和**各特征节点相对其依赖节点的条件概率表**。"
    )

    b.md(
        "### 📍 Workshop 钩子（重要！）\n\n"
        "**链式贝叶斯网 ⟺ 自回归语言模型**。Day 4 你写 nanoGPT 时，把一句话的概率分解成：\n\n"
        "$$P(w_1, w_2, \\ldots, w_n) = P(w_1) \\cdot P(w_2 \\mid w_1) \\cdot P(w_3 \\mid w_1, w_2) \\cdots P(w_n \\mid w_1, \\ldots, w_{n-1})$$\n\n"
        "这就是一个**线性链贝叶斯网**——每个 token 节点只指向后面所有 token。\n"
        "「causal mask（因果掩码）」在 self-attention 里阻止 token 看到未来——本质就是强制这种 DAG 结构。\n"
    )

    b.md(
        "### §3.1.1 贝叶斯网的独立性\n\n"
        "**局部独立性**：给定父节点条件下，每个节点都独立于它的非后代节点。"
        "例如给定父节点 $c$ 时，$e$ 与网中其他节点条件独立（$e \\perp a, b, d \\mid c$）。\n\n"
        "**全局独立性 (d-分离)**：d-分离是用来判断变量是否条件独立的图形化方法。常见于三种条件独立的情况：\n\n"
        "**1. tail-to-tail（共同原因）** `a ← c → b`\n"
        "- 不观察 $c$：$P(a, b) = \\sum_c P(a \\mid c) P(b \\mid c) P(c) \\neq P(a) P(b)$ → 不独立\n"
        "- **观察 $c$**：$P(a, b \\mid c) = P(a \\mid c) P(b \\mid c)$ → 条件独立 ✓\n\n"
        "**2. head-to-tail（链）** `a → c → b`\n"
        "- 不观察 $c$：不独立\n"
        "- **观察 $c$**：条件独立 ✓\n\n"
        "**3. head-to-head（V 型 / 碰撞节点）** `a → c ← b`\n"
        "- **不观察 $c$**：$P(a, b) = P(a) P(b)$ → 独立 ✓（关键！「碰撞节点不观察就独立」）\n"
        "- 观察 $c$：$P(a, b \\mid c) \\neq P(a \\mid c) P(b \\mid c)$ → 反而**不独立**（「explain away 现象」）\n\n"
        "**通用 d-分离判别**（对集合 $A, B, C$ 是否条件独立）：\n"
        "考虑图中所有 $A$ 和 $B$ 之间的路径。如果路径中存在 $X$：\n"
        "1. $X$ 是 head-to-tail 或 tail-to-tail，且 $X \\in C$ → 该路径阻塞\n"
        "2. $X$ 是 head-to-head，且 $X$ 或 $X$ 的儿子**不在** $C$ 中 → 该路径阻塞\n\n"
        "如果 $A, B$ 间所有路径都阻塞 → $A, B$ 关于 $C$ 条件独立。\n"
    )

    b.md(
        "### 朱明超原文：用 pgmpy 建一个 5 节点贝叶斯网\n\n"
        "**注意 API 变化**：朱明超原文是 2020 年代码，用 `pgmpy.models.BayesianModel`。"
        "pgmpy 1.0+ 改名为 `DiscreteBayesianNetwork`（功能一样）——我们用新名字。\n"
    )
    b.code(
        "import networkx as nx\n"
        "from pgmpy.models import DiscreteBayesianNetwork   # 朱原文是 BayesianModel\n"
        "from pgmpy.factors.discrete import TabularCPD\n\n"
        "# 建立一个简单贝叶斯模型框架：a→b, a→c, b→c, b→d, c→e\n"
        "model = DiscreteBayesianNetwork([('a', 'b'), ('a', 'c'), ('b', 'c'), ('b', 'd'), ('c', 'e')])\n\n"
        "# 最顶层 a 的先验\n"
        "cpd_a = TabularCPD(variable='a', variable_card=2, values=[[0.6], [0.4]])   # a: (0,1)\n"
        "# b 的条件概率：给定 a 的取值（行 = b 值，列 = a 值）\n"
        "cpd_b = TabularCPD(variable='b', variable_card=2,\n"
        "                   values=[[0.75, 0.1],\n"
        "                           [0.25, 0.9]],\n"
        "                   evidence=['a'], evidence_card=[2])\n"
        "# c 的条件概率：给定 (a, b) 联合\n"
        "cpd_c = TabularCPD(variable='c', variable_card=3,\n"
        "                   values=[[0.3, 0.05, 0.9,  0.5],\n"
        "                           [0.4, 0.25, 0.08, 0.3],\n"
        "                           [0.3, 0.7,  0.02, 0.2]],\n"
        "                   evidence=['a', 'b'], evidence_card=[2, 2])\n"
        "cpd_d = TabularCPD(variable='d', variable_card=2,\n"
        "                   values=[[0.95, 0.2],\n"
        "                           [0.05, 0.8]],\n"
        "                   evidence=['b'], evidence_card=[2])\n"
        "cpd_e = TabularCPD(variable='e', variable_card=2,\n"
        "                   values=[[0.1, 0.4, 0.99],\n"
        "                           [0.9, 0.6, 0.01]],\n"
        "                   evidence=['c'], evidence_card=[3])\n\n"
        "model.add_cpds(cpd_a, cpd_b, cpd_c, cpd_d, cpd_e)\n"
        "print('模型一致性检验:', model.check_model())\n\n"
        "# 画图\n"
        "plt.figure(figsize=(7, 5))\n"
        "nx.draw(model, with_labels=True, node_size=1500, node_color='lightyellow',\n"
        "        font_weight='bold', font_size=14, edge_color='gray',\n"
        "        pos={'a': (2, 5), 'b': (5, 5), 'c': (3, 3), 'd': (7, 3), 'e': (3, 1)})\n"
        "plt.title('贝叶斯网示例（朱明超原文图 1）')\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 3.E1：手算因子分解 P(a, b, c)\n\n"
        "用上面建好的贝叶斯网（无 $d, e$），手算 $P(a=0, b=0, c=0)$（按链式分解）。\n\n"
        "**公式**：$P(a=0, b=0, c=0) = P(a=0) \\cdot P(b=0 \\mid a=0) \\cdot P(c=0 \\mid a=0, b=0)$\n"
    )
    b.code(
        "# 从 CPT 表里读出对应的条件概率值\n"
        "P_a0 = 0.6                          # cpd_a values[[0.6], [0.4]]，a=0 的概率\n"
        "P_b0_given_a0 = 0.75                # cpd_b values[0][0]，给定 a=0 时 b=0\n"
        "P_c0_given_a0b0 = 0.3               # cpd_c values[0][0]，给定 (a=0,b=0) 时 c=0\n\n"
        "P_abc = P_a0 * P_b0_given_a0 * P_c0_given_a0b0\n"
        "print(f'P(a=0, b=0, c=0) = {P_abc:.4f}')\n"
        "# 0.6 * 0.75 * 0.3 = 0.135\n"
        "checks.assert_close('3.E1 P(a=0,b=0,c=0)', P_abc, 0.135)"
    )

    b.md(
        "### ✏️ 例题 3.E2：用 pgmpy 做条件独立查询\n\n"
        "**任务**：用 pgmpy 检查 「$a$ 和 $d$ 是否在给定 $e$ 时条件独立」（朱明超原文的例子）。\n\n"
        "**朱原文的人脑分析**：从 a 到 d 有两条路径——\n"
        "- `a→b→d`：$b$ 是 head-to-tail，**不在** $e$ 的集合中 → 不阻塞\n"
        "- `a→c→b→d`：$c$ 是 head-to-tail 不在集合中，$b$ 也不在集合中 → 不阻塞\n\n"
        "所以 a 和 d **不是**关于 e 条件独立的。\n"
    )
    b.code(
        "# pgmpy 的 d-separation API\n"
        "print('a ⊥ d | {} ?:', model.is_dconnected('a', 'd', observed=[]))   # True = 不独立\n"
        "print('a ⊥ d | {b} ?:', not model.is_dconnected('a', 'd', observed=['b']))\n"
        "print('a ⊥ d | {e} ?:', not model.is_dconnected('a', 'd', observed=['e']))\n\n"
        "# 给定 b 阻塞了 a-b-d 路径，且 a-c-b-d 路径里 b 也阻塞 → 条件独立\n"
        "indep_given_b = not model.is_dconnected('a', 'd', observed=['b'])\n"
        "checks.assert_true('3.E2 a ⊥ d | b', indep_given_b)\n"
        "# 给定 e 不阻塞（朱明超原文结论）→ 不独立\n"
        "indep_given_e = not model.is_dconnected('a', 'd', observed=['e'])\n"
        "checks.assert_true('3.E2 a 和 d 给定 e 不独立', not indep_given_e)"
    )

    # §3.2 无向图模型
    _yuanwen(
        b,
        "§3.2 无向图模型 (Undirected Model) — 马尔可夫网",
        "无向图模型的概率可以记作 $P(\\boldsymbol{x}) = \\frac{1}{Z} \\prod_{C \\in \\mathbf{Q}} \\Phi_C(\\boldsymbol{x}_C)$。"
        "其中，我们将所有节点都彼此联通的集合称作**团 (Clique, C)**，$\\Phi$ 称作**因子 (factor)**，"
        "每个因子和一个团 C 相对应，Z 是归一化常数。"
        "示例：$P(a, b, c, d, e) = \\frac{1}{Z} \\Phi^{(1)}(a, b, c) \\Phi^{(2)}(b, d) \\Phi^{(3)}(c, e)$。\n\n"
        "**有向图的代表是马尔可夫网**（错——这是朱原文笔误，应该是「无向图的代表」）。\n\n"
        "贝叶斯网是根据节点依赖关系构成有向无环图，进而引申出每个节点的条件概率分布来表征其对父节点的依赖。"
        "但马尔可夫网节点间的**依赖关系是无向的**（相互平等的关系），无法用条件概率分布来表示，"
        "为此引入**极大团**概念，进而为每个极大团引入一个**势函数 (Potential Function)** 作为因子，"
        "然后将联合概率分布表示成这些因子的乘积再归一化，归一化常数被称作**配分函数 (Partition Function)**。\n\n"
        "**团**：假设一个特征集的任何两个特征都互相关联，那么这个特征集的联合概率分布是无法简化的，"
        "我们称这样的特征集为团。\n\n"
        "**极大团**：如果一个团不能被其他团包含，那么我们称这个团为极大团。\n\n"
        "对于具有 $n$ 个特征变量 $\\boldsymbol{x} = (x_1, \\ldots, x_n)$ 的马尔可夫网的所有极大团构成的集合 $\\mathbf{Q}$，"
        "与极大团 $C \\in \\mathbf{Q}$ 对应的属性变量集合记作 $\\boldsymbol{x}_C$：\n\n"
        "$$P(\\boldsymbol{x}) = \\frac{1}{Z} \\prod_{C \\in \\mathbf{Q}} \\Phi_C(\\boldsymbol{x}_C), \\quad "
        "Z = \\sum_{\\boldsymbol{x}} \\prod_{C \\in \\mathbf{Q}} \\Phi_C(\\boldsymbol{x}_C)$$\n\n"
        "势函数可以写作 $\\Phi(\\boldsymbol{x}_C) = \\exp(-E(\\boldsymbol{x}_C))$，其中 $E$ 为**能量函数**，"
        "我们也称 $P(\\boldsymbol{x})$ 是由因子集 $\\{\\Phi_C \\mid C \\in \\mathbf{Q}\\}$ 参数化的"
        "**吉布斯分布 (Gibbs Distribution)** 或**玻尔兹曼分布 (Boltzmann Distribution)**。\n\n"
        "**马尔可夫网的条件独立性**：\n"
        "- **局部马尔可夫性**：将节点 $v$ 的所有邻接节点集作为分离集 $N(v)$，"
        "则节点 $v$ 与被邻接变量集分离的剩余变量集是条件独立的：$x_v \\perp \\boldsymbol{x}_{V \\setminus N^*(v)} \\mid \\boldsymbol{x}_{N(v)}$\n"
        "- **成对马尔可夫性**：两个非邻接节点 $u, v$，必然可以被其他所有节点构成的集 $\\boldsymbol{x}_{V \\setminus \\{u, v\\}}$ 分离，"
        "进而 $u, v$ 也具有条件独立性：$x_u \\perp x_v \\mid \\boldsymbol{x}_{V \\setminus \\{u, v\\}}$"
    )

    b.code(
        "# 朱明超原文马尔可夫网示例：a-b, a-c, b-c, b-d, c-e（无向边）\n"
        "from pgmpy.models import DiscreteMarkovNetwork   # 朱原文是 MarkovModel；pgmpy 1.1+ 用 Discrete 前缀\n"
        "from pgmpy.factors.discrete import DiscreteFactor\n\n"
        "model_mn = DiscreteMarkovNetwork([('a', 'b'), ('a', 'c'), ('b', 'c'), ('b', 'd'), ('c', 'e')])\n\n"
        "# 各团因子（势函数）：随机参数\n"
        "np.random.seed(0)\n"
        "factor_abc = DiscreteFactor(['a', 'b', 'c'], cardinality=[2, 2, 2], values=np.random.rand(8))\n"
        "factor_bd  = DiscreteFactor(['b', 'd'],      cardinality=[2, 2],    values=np.random.rand(4))\n"
        "factor_ce  = DiscreteFactor(['c', 'e'],      cardinality=[2, 2],    values=np.random.rand(4))\n"
        "model_mn.add_factors(factor_abc, factor_bd, factor_ce)\n"
        "print('马尔可夫网一致性:', model_mn.check_model())\n\n"
        "plt.figure(figsize=(7, 5))\n"
        "nx.draw(model_mn, with_labels=True, node_size=1500, node_color='lightyellow',\n"
        "        font_weight='bold', font_size=14, edge_color='gray',\n"
        "        pos={'a': (2, 5), 'b': (5, 5), 'c': (3, 3), 'd': (7, 3), 'e': (3, 1)})\n"
        "plt.title('马尔可夫网示例（朱明超原文图 3）')\n"
        "plt.show()"
    )

    b.md(
        "### ✏️ 例题 3.E3：识别极大团\n\n"
        "上面这个无向图（边集：a-b, a-c, b-c, b-d, c-e），有几个极大团？分别是哪些？\n\n"
        "**先在纸上画一下**：哪些节点彼此完全连通？\n"
    )
    b.code(
        "# 让 networkx 直接找极大团\n"
        "G = nx.Graph([('a', 'b'), ('a', 'c'), ('b', 'c'), ('b', 'd'), ('c', 'e')])\n"
        "max_cliques = list(nx.find_cliques(G))\n"
        "print('所有极大团:')\n"
        "for c in max_cliques:\n"
        "    print(f'  {sorted(c)}')\n"
        "# 应得: [a, b, c]（三角形）, [b, d]（边）, [c, e]（边）\n"
        "checks.assert_true('3.E3 共 3 个极大团', len(max_cliques) == 3)\n"
        "checks.assert_true('3.E3 三角形 {a,b,c} 在内',\n"
        "                   any(set(c) == {'a', 'b', 'c'} for c in max_cliques))"
    )

    b.md(
        "### 收尾：图模型在花书后续的角色\n\n"
        "本节只是**点了个名**。完整的图模型主题在花书 Ch 16 才展开。现在你应该带走的核心 takeaways：\n\n"
        "1. **联合分布因子分解**是图模型的灵魂 —— 把指数级参数降到线性\n"
        "2. **DAG → 贝叶斯网**：箭头表示因果/依赖；自回归语言模型本质就是链式贝叶斯网\n"
        "3. **无向图 → 马尔可夫网**：用势函数 + 配分函数；玻尔兹曼机 / 能量模型属于这类\n"
        "4. **d-分离的三种结构**：tail-to-tail、head-to-tail、head-to-head — 记住「碰撞节点不观察才独立」最反直觉\n\n"
        "📍 **Workshop 之后会再见**：扩散模型（forward = 链式马尔可夫，每步加 Gaussian 噪声）、VAE 的 latent 变量图模型。\n"
    )


def ch03_checkpoint(b: Builder):
    b.md(
        "---\n\n## CHECKPOINT — 本章自检\n\n"
        "在下面打勾（双击 cell 进编辑模式，把 `[ ]` 改成 `[x]`）：\n\n"
        "**§1 概率**\n\n"
        "- [ ] 能用一句话说清频率派 vs 贝叶斯派的差别\n"
        "- [ ] 知道 PMF 输出是概率，PDF 输出是密度（可 > 1），区间概率要积分\n"
        "- [ ] 给一张联合分布表，能秒算边缘 + 条件 + 判断独立性\n"
        "- [ ] 能默写期望 / 方差 / 协方差定义；知道 `np.var(ddof=0/1)` 和 `np.cov` 默认 ddof 的区别\n"
        "- [ ] 知道协方差 = 0 不蕴含独立（构造反例 $y = x^2$）\n\n"
        "**七大分布（§1.5）**\n\n"
        "- [ ] 看到分布名能回忆形状 + 用途：Bernoulli / Multinoulli / Gaussian / 多元 Gaussian / Exponential / Laplace / Dirac\n"
        "- [ ] 能手写**数值稳定的 softmax**（先减 max 再 exp）\n"
        "- [ ] 知道经验分布 $\\hat{p}_{\\text{data}}$ = 一堆 Dirac 函数的等权和\n\n"
        "**§1.6 函数**\n\n"
        "- [ ] 能默写 $\\sigma(x) = 1/(1+e^{-x})$ 和 $\\zeta(x) = \\log(1+e^x)$\n"
        "- [ ] 知道关键性质 $\\sigma(-x) = 1 - \\sigma(x)$ 和 $\\zeta'(x) = \\sigma(x)$\n\n"
        "**§2 信息论（最重要）**\n\n"
        "- [ ] **能默写自信息 $I(x) = -\\log P(x)$ + 香农熵 $H(P) = -\\mathbb{E}_P[\\log P]$**\n"
        "- [ ] **能默写 $D_{\\mathrm{KL}}(P\\|Q) = \\mathbb{E}_P[\\log P - \\log Q]$ + 交叉熵 $H(P,Q) = H(P) + D_{\\mathrm{KL}}(P\\|Q)$**\n"
        "- [ ] 知道 KL 不对称：正向 KL（覆盖型）vs 反向 KL（挑峰型）\n"
        "- [ ] 知道 RLHF 的 β·KL penalty 角色 + 「MLE = 最小化交叉熵」连接（**Workshop Day 1-2 立刻用到**）\n\n"
        "**§3 图模型**\n\n"
        "- [ ] 能默写贝叶斯网因子分解公式 $P(x) = \\prod_i P(x_i \\mid \\mathrm{PA}(x_i))$\n"
        "- [ ] 知道 d-分离的三种结构 + 「碰撞节点不观察才独立」反直觉点\n"
        "- [ ] 能把自回归 LM 看作链式贝叶斯网\n"
    )
    b.code("checks.report()")


# =========================================================
# Build & save ch03 demo + work
# =========================================================

def build_ch03():
    b = Builder()
    ch03_header(b)
    ch03_p1_1_concept(b)
    ch03_p1_2_distribution(b)
    ch03_p1_3_conditional(b)
    ch03_p1_4_measures(b)
    ch03_p1_5_dists(b)
    ch03_p1_6_funcs(b)
    ch03_p2_info_theory(b)
    ch03_p3_graphical(b)
    ch03_checkpoint(b)
    write_ipynb(b.demo, "ch03-probability/ch03.ipynb")
    write_ipynb(b.work, "ch03-probability/ch03_work.ipynb")


def main():
    print("Building notebooks...")
    build_template()
    build_ch02()
    build_ch03()
    print("Done.")


if __name__ == "__main__":
    main()
