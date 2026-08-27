# blossom — 花书交互式 Jupyter 学习

把《Deep Learning》（Goodfellow et al.，花书）每章核心内容做成可填空、可调参、可即时验证的 Jupyter notebook。形式参考 STAT200_In_R 的"读一段→动手填空→看 ✅"教学循环。

## 章节导航

| 章 | 主题 | demo（含答案） | work（学生填空版） | 状态 |
|---|------|---------------|------------------|------|
| 2 | 线性代数 | [ch02.ipynb](ch02-linear-algebra/ch02.ipynb) | [ch02_work.ipynb](ch02-linear-algebra/ch02_work.ipynb) | ✅ 已完成 |
| 3 | 概率与信息论 | [ch03.ipynb](ch03-probability/ch03.ipynb) | [ch03_work.ipynb](ch03-probability/ch03_work.ipynb) | ✅ 已完成 |
| 4+ | 数值计算 / 机器学习基础 / ... | — | — | 待 |

每章是一个独立子目录，包含：
- `chXX.ipynb`：**只读 demo 副本**，含完整答案、解释、可视化（chmod 444）
- `chXX_work.ipynb`：**只读填空教材**，里面有 `___` 和 ✅/❌ 自动检验（chmod 444）
- `chXX_attempt.ipynb`：**学生跑 `new_attempt.py` 复制出来的可写副本**——在这里做题
- `data/`：章内合成数据
- `figures/`：生成图缓存（gitignored）

> 教材副本（demo/work）是只读的，rebuild 不会覆盖你的 `chXX_attempt.ipynb` 进度。

## 如何开始

### 一次性环境配置（用 [uv](https://docs.astral.sh/uv/)）

```bash
cd blossom
uv sync                # 装 numpy / matplotlib / ipywidgets / jupyterlab / sklearn
uv run jupyter lab     # 启动 Jupyter Lab
```

不用 uv 也行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
jupyter lab
```

### 学习流程（每章）

**两个生成的 `.ipynb` 都是只读教材副本**（rebuild 时自动 `chmod 444`），不在它们上面做题。

1. **复制一份可写的 attempt 副本**：
   ```bash
   python3 scripts/new_attempt.py ch02
   # → ch02-linear-algebra/ch02_attempt.ipynb（可写）
   ```
2. 在 VS Code 里打开 `ch02_attempt.ipynb`，从顶部开始顺序读
3. 遇到 📖 **花书原文**——先看原文怎么定义（朱明超精读版）
4. 进入 blossom 的教学化展开，遇到 `___` 填空就填，遇到 ✏️ **例题** 就动手
5. 跑 cell 看 `checks.assert_*` 输出的 ✅ 或 ❌
6. 卡住时再开只读的 `ch02.ipynb`（demo）对照答案
7. 最后跑章末 CHECKPOINT 清单 + `checks.report()`

### 重置 attempt 副本

想推倒重做：

```bash
# 直接覆盖（会丢已填进度）
python3 scripts/new_attempt.py ch02 -f

# 或者给副本起个不同的名字保存多次尝试
python3 scripts/new_attempt.py ch02 --name pass2
# → ch02_pass2.ipynb
```

### 看完答案后想再过一遍

```bash
python3 scripts/new_attempt.py ch02 --from-demo --name review
# → 基于 demo（含答案）的副本，复习用
```

## 目录布局

```
blossom/
├── README.md                      # 本文件
├── pyproject.toml                 # uv 管理依赖
├── .python-version                # 锁 3.11
├── .gitignore
├── ch02-linear-algebra/
│   ├── ch02.ipynb                 # demo
│   ├── ch02_work.ipynb            # work
│   ├── data/                      # 合成数据
│   └── figures/                   # 生成图（gitignored）
├── templates/
│   └── _chapter_template.ipynb    # 通用 7 段骨架（供新章节复制）
├── utils/
│   ├── __init__.py
│   ├── checks.py                  # assert_equal / assert_shape / assert_close
│   └── viz.py                     # plot_vectors / plot_matrix_action / plot_eigen / ...
├── notebooks-meta/
│   └── obsidian_link_map.md       # notebook ↔ vault notio 双向索引
└── scripts/
    ├── build.py                   # 单一来源——重新生成所有 notebook
    └── fix_quotes.py              # 一次性工具（不再用）
```

## 每章的结构（跟书走，不是套模板）

**章节内部结构跟着花书拆解里对应章节的原文（朱明超精读版）走**——书有几节，blossom 就有几节。
例如 Ch 2 是按朱明超 §1（标量/向量/矩阵/张量）→ §2（转置）→ ... → §10（PCA）十节组织的，
每节内嵌入原文 + blossom 在原文之上做教学化展开（直觉、NumPy 手写、可视化、填空、例题、错误反例）。

每节的「学习视角」尽可能多覆盖：
- 📖 **原文嵌入** — 先看朱明超对花书原文的精读怎么定义
- 直觉 / 几何 / 类比
- NumPy 手写（for 循环 + `np.linalg.*` 一行对照）
- 填空 + `checks.assert_*` 立即反馈
- 预测题：先猜再跑
- 必要时可视化、错误反例、后续章节轻量预告

> Ch 2 因为是第一章做的，留下了 blossom 自创的 Sec 0–8 结构（作为历史包袱保留）；
> Ch 3 起按上面的「跟原文走 + 多视角」原则。

例题分四种类型：**填空**（`___`，配自动断言）/ **预测题**（先猜再跑）/ **改造题**（小重构）/ **YOUR TURN**（开放）。

## 与 vault 的链接

- notebook → vault：markdown 链接用 `obsidian://open?vault=Cementine%20Vault&file=...` URI，点击在 Obsidian 中打开
- vault → notebook：相关 notio（[张量]、[矩阵乘法]、[Hadamard 乘积]、[Einstein 求和约定]、[张量语言]）的"配套 notebook"行回链此项目
- 双向索引：`notebooks-meta/obsidian_link_map.md`

## 验证（每章完成后跑）

```bash
# demo 全部 cell 能跑通
jupyter nbconvert --execute --to notebook --inplace ch02-linear-algebra/ch02.ipynb

# git 应该干净（figures/、checkpoints/ 都被忽略）
git status
```

## 内容来源声明

所有讲解和代码原创（基于公开数学知识）；参考 Goodfellow et al. *Deep Learning* 的章节组织和概念顺序，但**不复制书中文字**。技术细节实现来自标准 NumPy / 线性代数教学惯例。MingchaoZhu/DeepLearning（GitHub）作为内容编排顺序的参考来源。

## 后续

Ch 3+ 在 Ch 2 跑完一遍 + 反馈后用同一套模板扩展。
