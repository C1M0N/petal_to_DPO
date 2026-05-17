# blossom — 项目宪章（给下任 Claude）

如果你是新接手这个项目的 Claude session，**先把这份文件从头读到尾**。它把"该怎么做事"全说清楚了，不要重新发明轮子。

## 项目是什么

`blossom/` 是花书（Goodfellow et al. *Deep Learning*）的**交互式 Jupyter 学习项目**。每章产出两个 notebook：

- `chXX.ipynb`：**demo 副本**——含完整答案、解释、可视化（用户对照看）
- `chXX_work.ipynb`：**学生工作副本**——填空 + 空 cell + `checks.assert_*` 自动验证

形式参考用户在 STAT200 课学到的 R 教学项目（"读一段 → 立刻动手 → 看 ✅ 红绿灯"）。内容参考**花书拆解文件夹里的内容**

落地在用户的 AI-303 课程项目仓库 `petal_to_DPO/` 下作为一个模块。

## 用户上下文（关键）

- PSU 在读 CS 学生，数学双学位 + 神经科学辅修
- 数学（含线代(但较为薄弱)）基础有，但**几乎没用过 NumPy / Jupyter**——把他当"完全新手"对待
- 主要工具：**VS Code**（不是 Jupyter Lab），看到 Jupyter Lab 的快捷键提示会困惑
- 习惯中文交流；技术术语保留英文原文
- 不喜欢被替代——你给的解释他要能跟着推理；不要只给结论
- 用户全局规则（继承自 `~/.claude/CLAUDE.md`）：
  - **禁止 AI 署名**：git commit 不加 `Co-Authored-By`
  - 用中文回答
  - 创建文件前先核实路径
  - 不要改动已验证的格式（已有 wikilink / 命名等不要"优化"）
  - 不自动 commit，只能用 `/cmm` 触发
  - 宪章度（devil 度）7/10——主动挑战盲点，但不要钳制创新

## 目录布局

```
blossom/
├── CLAUDE.md                       ← 你正在读
├── README.md                       学习者用的入口
├── pyproject.toml                  uv 依赖锁
├── .python-version                 锁 3.11
├── .gitignore                      ipynb_checkpoints / figures / .venv
├── 花书拆解                          内含所有每章附有代码小demo的花书原文
│   ├── 配套代码                      部分章节的配套代码
│   ├── 重要章节                      你需要jupyter化教学化例题化的内容(需要你把原文也写在jupyter的markdown部分)
├── ch02-linear-algebra/
│   ├── ch02.ipynb                  生成产物：demo（含答案）
│   ├── ch02_work.ipynb             生成产物：work（填空）
│   ├── data/                       章内合成数据（目前空）
│   └── figures/                    matplotlib 图缓存（gitignored）
├── ch03-probability/               待建（按模板复制）
├── ...
├── templates/
│   └── _chapter_template.ipynb     14 cell 通用骨架
├── utils/
│   ├── __init__.py
│   ├── checks.py                   assert_equal / assert_shape / assert_close / report
│   └── viz.py                      plot_vectors / matrix_action / eigen / tensor_slices / points_2d
├── notebooks-meta/
│   └── obsidian_link_map.md        notebook ↔ vault notio 双向索引
└── scripts/
    ├── build.py                    ★ 单一来源 — 改它，重跑它（生成的 ipynb 自动 chmod 444 只读）
    ├── new_attempt.py              复制一份可写的学习副本（chXX_attempt.ipynb）给学生做题
    └── fix_quotes.py               一次性工具（不要再跑——曾经搞坏过文件）
```

## 单一来源：`scripts/build.py`

**所有 notebook 都从 `build.py` 生成。永远不要手改 `.ipynb`！**

重跑命令：

```bash
cd blossom
python3 scripts/build.py
```

这会重新生成：

- `templates/_chapter_template.ipynb`（通用骨架，~14 cells）
- `ch02-linear-algebra/ch02.ipynb`（demo，161 cells）
- `ch02-linear-algebra/ch02_work.ipynb`（work，161 cells）

### `build.py` 的核心 API

```python
b = Builder()
b.md("markdown 内容...")               # 在 demo 和 work 副本里加同一个 md cell
b.code("正确答案代码")                  # demo == work 一致
b.code("正确答案", work_src="填空版")    # demo 给答案；work 给 ___
```

每章一个 `chXX_section(b)` 函数（如 `ch02_sec0`、`ch02_sec1`...），最后在 `build_chXX()` 里串起来。

### ⚠️ 学生工作流：只读教材 + 可写 attempt

为了避免 rebuild 覆盖学生进度，**生成的 `chXX.ipynb` 和 `chXX_work.ipynb` 都被双重锁定**：
1. `chmod 444`（POSIX 只读）
2. `chflags uchg`（macOS user-immutable flag）—— 这条是关键

**为什么需要 uchg**：单独 `chmod 444` 时，VS Code 看到文件**仍允许在内存里编辑 cell**，只在保存时弹"覆盖只读？"对话框——这对学生体验不够严格（很容易忽视弹框、改完发现保存不下去才疑惑）。加上 `chflags uchg` 后，OS 层面**直接拒绝任何写入**（错误信息从 "permission denied" 变成 "operation not permitted"），VS Code 会真正放弃保存。

`build.py` 写入前会先 `chflags nouchg` 解锁，写完再加回去——所以 rebuild 始终能正常工作。

要做题学生跑：
```bash
python3 scripts/new_attempt.py ch02
```
这会复制一份**可写**的 `ch02_attempt.ipynb`（权限 0o644，无 uchg），学生在 attempt 副本上填空、做题。rebuild 不会动 attempt 文件。

每次 rebuild 之前你只需提醒用户：「重跑会更新 `ch02.ipynb` 和 `ch02_work.ipynb`（只读教材副本），你的 `ch02_attempt.ipynb` 不受影响」。

**Linux 用户注意**：`chflags` 是 BSD/macOS 独有的。build.py 在非 macOS 上**只做 chmod 444**——VS Code 仍可能允许 in-memory 编辑。Linux 等价机制是 `chattr +i`，但需要 root，所以没加；如果未来要支持 Linux 严格锁，需要研究替代方案。

## 章节内部结构（跟着原文走，不强加模板）

**核心原则**：每章的**内部结构跟随花书拆解里对应章节的朱明超精读版原文**——
书有几节，blossom 就有几节。**不强加统一模板**。

例如：
- **Ch 2（线性代数）**：原文有 §1 标量/向量/矩阵/张量、§2 转置、§3 加法、§4 矩阵乘法、§5 单位矩阵、§6 逆、§7 范数、§8 特征分解、§9 SVD、§10 PCA——blossom 就按这 10 节组织（每一节 = 原文嵌入 + blossom 教学化展开）
- **Ch 3（概率与信息论）**：按朱明超 Ch 3 原文的小节走
- 其他章同理

### 每一节内部的「教学化展开」——尽可能覆盖多个学习视角

每节不是只把原文贴上去就完事。要让学生从多个角度反复啃同一个概念，**视角越多消化越深**。可用的视角（**不强求每节全用**，按内容裁剪）：

1. **📖 原文嵌入**：朱明超对应小节的原文 + 配套代码作为「底本」放在节的开头。学生**先看原文怎么定义**。
2. **直觉 / 几何 / 类比**：用自己的话说「这对象是什么、为什么这么定义」。
3. **NumPy 手写**：每个算子 → for 循环手写 → `np.linalg.*` 一行验证 → 对比。
4. **填空 + 自动验证**：`x = np.___(...)` + `checks.assert_*` 立即 ✅/❌ 反馈。
5. **预测题**：让学生先猜（输出 shape / 数值），再跑验证。
6. **可视化**：必要时用 matplotlib 画出抽象对象（向量、变换、特征向量、张量切片）。
7. **错误案例 / 反例**：构造「为什么这个会挂」的例子（如非方阵不能 `np.linalg.eig`）。
8. **后续章节预告（轻量）**：一句话提「这个工具后面 Ch X 会用作 Y」——**只贴标签，不展开**。

### 🚧 不要把后面章节的知识太往前提（铁律）

用户原话："**我是从 0 学习深度学习，有些东西在这一章就教我消化不了**"。

举例：
- ❌ Ch 2 阶段不要写完整的 weight decay 推导（依赖梯度下降）
- ❌ Ch 2 阶段不要塞 self-attention 公式 `softmax(QK^T/√d_k)V`（依赖 softmax、attention 概念）
- ❌ Ch 2 阶段不要讲 PPO clipping、Multi-Head Attention、LoRA 完整实现等

**允许的"后续预告"形式**：只贴名字 + 一句话用途。例如：
> 「$L^2$ 范数在花书 Ch 7 会用作 weight decay——加到 loss 里防止参数太大。详见 Ch 7。」

具体推导一律留给对应章节。

### CHECKPOINT 是每章硬性要求

每章末尾必须有 **CHECKPOINT 自检清单 + `checks.report()`**，至少 8 项。条目分两类：
- **核心**：本章重点的"能不能讲清/能不能写出来"
- **轻量预告（可选）**：知道后面会再相遇的工具名字即可

### Ch 2 是历史包袱

Ch 2 是第一章做的，留下了 blossom 自创的 "Sec 0–8 + CHECKPOINT" 结构。
原文 §1–§10 是后来「打散嵌入」到这些 Sec 里——属于**老结构 + 原文补丁**的混合产物。

**Ch 3 起按上面「跟原文走 + 多视角」的原则做**，不要再复制 Ch 2 的 Sec 0–8 结构。
Ch 2 的 Sec 命名不必整改（学生已经熟悉），但内部讲解要继续往「视角覆盖」方向迭代。

## 例题设计：四类混用

| 类型 | 形式 | 占比 |
|------|------|------|
| **填空题** | `x = np.___(...)`，配 `utils.checks.assert_*` 立即验证（绿/红） | ~60% |
| **预测题** | "运行**前**先猜：下面输出什么 shape？"→ 跑了验证 | ~15% |
| **改造题** | "修改下面代码让它实现 Y" | ~15% |
| **YOUR TURN** | 完全空 cell + markdown 任务描述 | ~10% |

### Hint 质量要求（**重要——用户曾抱怨过 hint 太薄**）

对**第一次接触某 NumPy 方法**的题，hint 必须：

- ❌ 不够：`# 提示：让形状变成 (784,)`（只告诉结果，没告诉 API）
- ✅ 够：`# 提示：NumPy 有三个方法能展平 1D —— .flatten() / .ravel() / .reshape(-1)，任选一个`

**判断原则**：用户能不能从 hint **加上前面 Sec 1-5 已讲过的知识**推出答案？能 → OK；不能 → 必须在 hint 里给 API 候选。

如果用户抱怨某 hint 不够，**就改 build.py 里那一题的 hint**（加 API 候选 / 概念名 / 例子），然后跟用户确认要不要 rebuild。

## 已学过的避坑

### 1. Python 字符串里的中文双引号

`build.py` 的 `b.md("...内容...")` 调用的内容里**不能有英文双引号 `"`**，会破 Python 字符串。

```python
# ❌ 坏 — Python 解析失败
b.md("**关键**：cell 的"显示顺序"≠"执行顺序"")

# ✅ 用中文引号 「」 替代
b.md("**关键**：cell 的「显示顺序」≠「执行顺序」")
```

历史：曾用 `scripts/fix_quotes.py` 一次性扫描修复——**别再跑那个脚本**，它会破坏 docstring（已经把 `"""..."""` 改成了奇形怪状）。直接在编辑时用 「」 就行。

### 2. VS Code 不会自动 reload .ipynb

用户在 VS Code 里开着 `ch02.ipynb`，你重跑了 `build.py` 覆盖磁盘文件——**VS Code tab 仍显示旧版**。

每次 rebuild 后必须告诉用户：

> Reload notebook：关掉 tab 重开，或 `Cmd+Shift+P` → `Revert File`

### 3. uv 环境 + kernel 选择

项目用 [uv](https://docs.astral.sh/uv/) 管理 venv：

```bash
cd blossom
uv sync                # 装齐依赖到 .venv/
uv run jupyter lab     # 或在 VS Code 选 .venv/bin/python 当 kernel
```

VS Code 用户**必须手动**选 kernel `blossom (3.11.x)`——不会自动切。

### 4. 重跑 build.py 的副作用

- 覆盖 `ch02_work.ipynb` → **学生进度丢失**
- 覆盖 `ch02.ipynb` → demo 重生成（一般无害）
- 不影响 `utils/`、`README.md`、`pyproject.toml`、`templates/_chapter_template.ipynb`（除非你也改了 build_template）

## 与 vault 的双向链接

用户的知识库在 `/Users/lainos/Dropbox/Ptolemaeus Studio/Cementine Vault`。

### notebook → vault：obsidian:// URI

```markdown
[张量](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E5%BC%A0%E9%87%8F)
```

中文 URL 编码注意：`/` → `%2F`、中文字符按 UTF-8 编码（用 `urllib.parse.quote` 算）。

### vault → notebook：notio 末尾的反向链接

Ch 2 涉及 5 个现有 notio（已经各自在末尾加了一行"📓 配套 notebook"）：

- `30 The Colonnade/张量.md`
- `30 The Colonnade/矩阵乘法.md`
- `30 The Colonnade/Hadamard 乘积.md`
- `30 The Colonnade/Einstein 求和约定.md`
- `30 The Colonnade/张量语言.md`

**新章节如果引用了 vault 已有 notio**，记得在 `notebooks-meta/obsidian_link_map.md` 更新对照表，并在对应 notio 末尾加配套 notebook 行。

### vault 的命名规范（如果你要建新 notio）

- 文件名默认中文（如 `张量.md`）；英文/原名/缩写/别名放 frontmatter 的 `aliases`
- 人名保留英文（如 `Einstein 求和约定.md`、`Erich Fromm.md`）
- 必备 frontmatter：`UID / type / status / updated / tags / summary / aliases / authors`
- notio 用 `type: notio`，放 `30 The Colonnade/`

不熟悉就**别去碰 vault 文件**；问用户先。

## 验证 checklist（每章完成后跑）

1. **JSON 可解析**：`python3 -c "import json; json.load(open('chXX.ipynb'))"` 无报错
2. **环境可装**：`uv sync` 完整跑过
3. **demo 可执行**：`jupyter nbconvert --execute --to notebook --inplace chXX-X/chXX.ipynb` 全跑通
4. **work 可学**（自己当陌生学生跑一遍）：
   - 所有 `___` 能根据 Sec 1-5 + hint 填出
   - 所有 `checks.assert_*` 输出 ✅
   - CHECKPOINT 打勾能全勾
5. **例题密度**：原则上每章 ≥ 30 个 ✏️ 例题（按原文小节数自然分布；不强求每节硬性配额——按原文长短裁剪）
6. **链接闭环**：obsidian:// URI 点击能开对应 notio；vault notio 的"配套 notebook"行存在
7. **git 干净**：`git status` 不显示 `.ipynb_checkpoints/`、`__pycache__/`、`figures/`

## 章节进度

| 章 | 主题 | 状态 |
|---|------|------|
| Ch 2 | 线性代数 | ✅ **已完成**（嵌入原文 §1–§10 + Sec 8 轻量预告；老 Sec 0–8 结构，作历史包袱保留）|
| Ch 3 | 概率论 | 待建 |
| Ch 4 | 数值计算 | 待建 |
| Ch 5 | 机器学习基础 | 待建 |
| Ch 6 | 深度前馈网络 | 待建（此章起加 PyTorch） |
| Ch 7 | 正则化 | 待建 |
| Ch 8 | 优化 | 待建 |
| Ch 9 | 卷积网络 | 待建 |
| Ch 11 | 实践方法论 | 待建 |

按 MingchaoZhu 已完成的 9 章为第一阶段范围（其他 11 章待后续视用户兴趣扩展）。

## 怎么加新章（Ch 3+ 标准流程）

1. **mkdir**：`mkdir -p chNN-topic/{data,figures}`
2. **读原文**：先完整读 `花书拆解/重要章节/N XXX.pdf`（朱明超精读版），**列出原文的全部小节** §1, §2, ...。这是新章的骨架。
3. **写 build.py 函数**：
   - 每章一个 `build_chNN()` 在末尾把所有小节串起来
   - 每节命名按原文小节走：`chNN_p1_xxx`、`chNN_p2_yyy`、...（不再用 `chNN_sec0..7` 这种 blossom 模板编号）
4. **每节内部走「多视角教学化展开」**：原文嵌入 → 直觉 → NumPy 手写 → 填空 → 预测 → 必要时可视化 → 必要时错误反例 → 后续预告（轻量）。
   能覆盖几个视角算几个，**不强求全覆盖**。
5. **章首加一句 Jupyter 速查的回链**："忘了 Jupyter 怎么用？回 ch02 看 Sec 0"——不重复教 Jupyter。
6. **章末必须**：CHECKPOINT 自检清单 + `checks.report()`。
7. **跑 build.py** 生成 `chNN.ipynb` + `chNN_work.ipynb`（自动 chmod 444 只读）。
8. **跑验证 checklist**。
9. **加 vault notio 双向链接**（如果引用了任何 notio）。
10. **不要自动 commit**——等用户用 `/cmm` 触发。

### 🚨 三条铁律

- **不要把后面章节的知识太往前提**（详见上面 § 章节内部结构）
- **不要重排原文逻辑顺序**——blossom 是「在原文之上加教学」，不是「重写花书」
- **不要复制 Ch 2 的 Sec 0–8 模板**——那是历史包袱

### Ch 6 起加 PyTorch

`pyproject.toml` 的 dependencies 加 `torch>=2.0`，然后 `uv sync`。

Ch 2-5 保持纯 NumPy（强化数学直觉）；Ch 6 起**双轨**：先 NumPy 手写一遍（看清反向传播机制），再 PyTorch 一行验证（承认工程现实）。

## 用户偏好 / 风格细节

- **不喜欢"完成 X" / "已完成 Y"末尾总结**——他能读 diff
- **需要像深度学习教授一样进行详细教学**——花书本身简概，需多写解释 + 多视角覆盖（直觉、几何、可视化、错误反例）
- **不要把后面章节的知识太往前提**——用户是从 0 学习深度学习，本章学不会的知识就不要塞进来。提到后续概念时**只贴名字**（"等你学到 Ch X 再回来看"），不展开
- **挑战度 7/10**：发现盲点就说出来（"花书这里其实没讲清楚 underlying set vs vector space"），但不要钳制创新（用户已下定决心的方向跟着走）
- **认知透明**：给推理链，不只给结论。"我选 3.11 是因为 PyTorch 官方 wheel 默认稳在 3.11 / 3.12"——把 why 说清
- **遇到事实性主张时主动核实**——基于 NATO Admiralty Code 方法论的 `/doubt` 思路（不要瞎信单一来源；交叉验证；不确定时说"不确定"）

## Git 工作流

`petal_to_DPO` 仓库是用户的 AI-303 课程项目。当前在 `develop` 分支。

- **不要主动 commit**——用户用 `/cmm` 触发；你只准备改动
- **绝不加 `Co-Authored-By`**（用户全局规则）
- commit 信息按用户惯例写中文+简洁说明

## 紧急 debug 提示

- **build.py 跑挂**：80% 是字符串里嵌套了 `"`——用 `「」` 替代
- **notebook 打不开**：JSON 格式坏了，`json.load` 复查；通常 `b.code()` 调用里有未转义的特殊字符
- **VS Code 没看到新内容**：reload tab；如果还不行 reload window
- **kernel 报 ipykernel 缺失**：用户选了 base / conda kernel——让他切到 `blossom (.venv/bin/python)`
- **断言全红**：检查 `utils/checks.py` 是否被导入——`from utils import checks, viz` 在 Sec 0 必须跑成功
