---
UID: 2026-0409-2331-f3e3
type: course
status: false
updated: 2026-05-17
tags:
  - ai-303
  - rlhf
  - dpo
  - reinforcement-learning
  - alignment
  - self-study
summary: "自学冲刺课：从数学基础到 RLHF/DPO 全链路，含 nanoGPT 和 Mini-DPO 实现"
aliases:
  - Agent Learning Workshop
authors:
  - Cimon Peng
---

# Agent Learning Workshop: RLHF, DPO & Online Adaptation

## Info

- 系号: [[{A-I} Artificial Intelligence|A-I]]
- 机构: [[Cementine Academy]]
- 前置要求: [[[CMPSC 132] Python与数据结构|CMPSC 132]], [[[MATH 220] 矩阵|MATH 220]], [[[MATH 414] 概率论导论|MATH 414]]
- 开始时间: 2026-05-18
- 结束时间: 2026-04-21

## Syllabus

- 形式: 两周冲刺（80h），独立学习
- 目标: 准备 RLHF/alignment 方向研究面试
- 教材: Goodfellow *Deep Learning* + Sutton & Barto *RL: An Introduction*
- 参考资料: `Belearning/A-I 303/`
- 阶段一（56h, 5/19–5/26）: 所有 deliverable 在 5/23 晚完成，留考试 buffer
- 阶段二（24h, 5/27–5/30）: 见教授后深度补强 + 面试准备

```
5/18 Thu ░░░░░░░░░░░░░░░ 0h   
		准备日
5/19 Fri ███░░░░░░░░░░░░ 3h   
		数学速攻
5/20 Sat ███████████████ 15h  
		数学全打通 + RL + PG + GoBeyond初探
5/21 Sun ███████████████ 15h  
		PPO→RLHF全线论文 + Karpathy + 语言反馈 + GoBeyond代码
5/22 Mon ██████████░░░░░ 10h  
		DPO精读 + nanoGPT + Text2Grad
5/23 Tue ██████████░░░░░ 10h  
		Mini-DPO全流程 + Memo + CV/邮件
5/24 Wed ░░░░░░░░░░░░░░░ 0h
		休息
5/25 Thu ░░░░░░░░░░░░░░░ 0h   
		休息
5/26 Fri ███░░░░░░░░░░░░ 3h   
		D-DAY：发邮件 + 见教授
─────────────── 阶段一 56h───────────────────────
5/27 Sat ██████████░░░░░ 10h  
		GoBeyond深入 + TRL + Goodfellow补遗 + Memo扩充
5/28 Sun ██████████░░░░░ 10h  
		B级论文 + 模拟面试 + Memo终稿 + 全面打磨
5/29 Mon ████░░░░░░░░░░░ 4h   
		最终准备 + 设备检查 + 概念卡片
5/30 Tue ████░░░░░░░░░░░ 3h
		面试
─────────────── 阶段二 24h───────────────────────总计 80h
```

## Deliverables

- [ ] **nanoGPT** — 从零实现 Transformer，push GitHub（Day 4, 5/22）
- [ ] **Mini-DPO** — 手写 DPO 训练（不用 TRL），push GitHub（Day 5, 5/23）
- [ ] **技术 Memo 初稿** — 3 页：DPO 推导 + Mini-DPO 实验 + 两条路线对比（Day 5, 5/23）
- [ ] **CV + 邮件终稿** — CV 加 nanoGPT + Mini-DPO，邮件附 GitHub + Memo PDF（Day 5, 5/23）
- [ ] **邮件发送** — 9 点前发出（Day 8, 5/26）
- [ ] **见教授** — 自我介绍 → Memo → 问项目期望 → 展示代码/推导（Day 8, 5/26）
- [ ] **技术 Memo 终稿** — 4-5 页，加入 GoBeyond 系统分析 + 参数 vs 非参数对比 + 融合可能性（Day 10, 5/28）
- [ ] **面试** — 5/30 下午

---

## Content

### Day 0 · 5/18 周四 · 0h · 准备日

写作业。睡前确认 Goodfellow 花书已准备好。

---

### Day 1 · 5/19 周五 · 3h · 数学速攻

#### M1: 信息论核心 — Goodfellow 3.13 + 3.10-3.11 (1h)

**自信息 → Shannon 熵 → 交叉熵 → KL 散度** 的推导链：

$$I(x) = -\log P(x)$$

$$H(P) = -\sum_x P(x) \log P(x)$$

$$H(P, Q) = -\sum_x P(x) \log Q(x)$$

$$D_{\mathrm{KL}}(P \| Q) = \sum_x P(x) \log \frac{P(x)}{Q(x)} = H(P, Q) - H(P) \geq 0$$

核心恒等式：$H(P, Q) = H(P) + D_{\mathrm{KL}}(P \| Q)$

常用函数：sigmoid $\sigma(x) = \frac{1}{1+e^{-x}}$，softplus $\zeta(x) = \log(1+e^x)$，softmax $\text{softmax}(z)_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$，贝叶斯规则

sigmoid 与 softmax 的关系：二分类时 softmax 退化为 sigmoid

#### M2: 概率基础 — Goodfellow 3.1-3.5 (1h)

概率公理、随机变量、PMF/PDF、边际概率、条件概率、链式法则：

$$P(x^{(1)}, \ldots, x^{(n)}) = P(x^{(1)}) \prod_{i=2}^{n} P(x^{(i)} \mid x^{(1)}, \ldots, x^{(i-1)})$$

#### M3: 线代快扫 — Goodfellow 2.1-2.5 (1h)

向量/矩阵/张量运算、线性相关与生成子空间、范数：

$$\|x\|_p = \left(\sum_i |x_i|^p\right)^{1/p}$$

L1 范数（稀疏性）、L2 范数（欧几里得距离）、Frobenius 范数

#### Day 1 Checklist

- [ ] $D_{\mathrm{KL}}(P \| Q)$ 定义能默写，能证明 $D_{\mathrm{KL}} \geq 0$（Jensen 不等式）
- [ ] 交叉熵 = 熵 + KL 散度
- [ ] sigmoid 和 softmax 的关系搞清
- [ ] 范数定义已复习

---

### Day 2 · 5/20 周六 · 15h · 数学全打通 + RL + PG + GoBeyond 初探

#### M4: 概率深入 — Goodfellow 3.6-3.9 (1.25h)

独立性与条件独立、期望/方差/协方差：

$$\mathbb{E}[X] = \sum_x x \, P(x), \quad \mathrm{Var}(X) = \mathbb{E}[(X - \mathbb{E}[X])^2]$$

常用分布：**Categorical**（= LM 输出分布）、**高斯** $\mathcal{N}(\mu, \sigma^2)$

#### M5: MLE 推导 — Goodfellow 5.1-5.2 + 5.4-5.5 (1.5h)

学习框架 + 容量/过拟合/欠拟合 + 偏差-方差权衡

最大似然估计：

$$\theta_{\mathrm{MLE}} = \arg\max_\theta \prod_{i=1}^m p_{\mathrm{model}}(x^{(i)}; \theta) = \arg\max_\theta \sum_{i=1}^m \log p_{\mathrm{model}}(x^{(i)}; \theta)$$

**MLE ⟺ 最小化交叉熵**（核心推导）：

$$\theta_{\mathrm{MLE}} = \arg\min_\theta H(\hat{p}_{\mathrm{data}}, p_{\mathrm{model}}) = \arg\min_\theta \left[-\mathbb{E}_{x \sim \hat{p}_{\mathrm{data}}} \log p_{\mathrm{model}}(x; \theta)\right]$$

#### M6: MAP + 监督学习 + SGD — Goodfellow 5.6-5.7 + 5.9 (1h)

MAP = MLE + 先验，与 RLHF 中 KL 正则的类比：

$$\theta_{\mathrm{MAP}} = \arg\max_\theta \left[\log p(\theta \mid x) \right] = \arg\max_\theta \left[\sum_i \log p(x^{(i)} \mid \theta) + \log p(\theta)\right]$$

MAP 中的 $\log p(\theta)$ 类似 RLHF 中的 $-\beta D_{\mathrm{KL}}[\pi_\theta \| \pi_{\mathrm{ref}}]$：都是"别离参考太远"

#### M7: 约束优化 — Goodfellow 4.3-4.4 (1h)

梯度下降 + **Lagrange 乘子法**：

$$\mathcal{L}(x, \lambda) = f(x) + \lambda \, g(x)$$

约束优化在 RLHF 中的角色：KL 约束就是一个 Lagrangian，$\beta$ 就是乘子

#### M8: 神经网络 — Goodfellow 6.1-6.4 + 6.2.1-6.2.2 (2.5h)

**代价函数 + 输出单元**：线性输出、sigmoid 输出、**softmax 输出**

softmax + cross-entropy 的数值稳定性：$\log \text{softmax}(z)_i = z_i - \log \sum_j e^{z_j}$

XOR 问题 + 隐藏单元（ReLU）+ 架构设计

#### M9: 反向传播 + 优化器 — Goodfellow 6.5.1-6.5.3 + 8.1 + 8.3 + 8.5 (1h)

反向传播：链式法则的计算图实现

学习 vs 优化的区别、SGD 动量、**Adam**：

$$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \quad v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$

$$\theta_{t+1} = \theta_t - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t} + \epsilon}$$

#### M10: RL 全景 — Lilian Weng 博客 + Sutton Ch 3 (3.75h)

Lilian Weng "A (Long) Peek into RL"：MDP、policy、reward、return 全景概念图

**Sutton & Barto 第 3 章 Finite MDPs**（精读，做习题 3.1-3.5）

MDP 五元组 $(S, A, P, R, \gamma)$

**Bellman 期望方程**：

$$v_\pi(s) = \sum_a \pi(a|s) \sum_{s', r} p(s', r \mid s, a) \left[r + \gamma \, v_\pi(s')\right]$$

**Bellman 最优方程**：

$$v_*(s) = \max_a \sum_{s', r} p(s', r \mid s, a) \left[r + \gamma \, v_*(s')\right]$$

#### M11: Policy Gradient 预读 — Sutton 13.1-13.2 (0.75h)

策略梯度基本思想 + 策略参数化

#### M12: 推导练习 (15min)

手写：KL 非负性证明 + MLE = 交叉熵推导 + Bellman 方程

#### M13: GoBeyond 初探 — README + models.py (1h)

通读 README，理解 7 步主循环：observe → update → retrieve → generate → rerank → predict → audit

`models.py` 核心数据结构：
- `BeliefState`（8 维）：对用户心理状态的实时估计
- `ValueProfile`（7 维）：用户价值观偏好
- `DialogueState`：scene / relation / topic / open_loops
- `ObservationSignals`：prediction error 驱动更新

#### Day 2 Checklist

- [ ] 能推导：MLE ⟺ 最小化交叉熵
- [ ] 能写出 RLHF KL 约束目标函数
- [ ] Lagrangian 能解释，$\beta$ 的角色能说清
- [ ] softmax + cross-entropy 关系搞清
- [ ] Bellman 方程能默写（期望 + 最优）
- [ ] **Goodfellow 第 2-6 章 + 第 8 章核心完成**
- [ ] Policy Gradient 基本概念已有
- [ ] GoBeyond 架构图能口述

---

### Day 3 · 5/21 周日 · 15h · PPO → RLHF → A 级论文 + Karpathy + 语言反馈 + GoBeyond 代码

#### M14: Policy Gradient 精读 — Sutton 13.3-13.4 (1.5h)

**REINFORCE** + baseline：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\pi_\theta}\left[\nabla_\theta \log \pi_\theta(a_t \mid s_t) \cdot (G_t - b(s_t))\right]$$

其中 $G_t = \sum_{k=0}^{\infty} \gamma^k r_{t+k+1}$ 是回报，$b(s_t)$ 是 baseline（通常为 value function），用于降低方差

#### M15: TRPO — Lilian Weng "Policy Gradient Algorithms" (1h)

信任域方法：限制每步策略更新的幅度

$$\max_\theta \; \mathbb{E}\left[\frac{\pi_\theta(a|s)}{\pi_{\theta_\mathrm{old}}(a|s)} \hat{A}(s,a)\right] \quad \text{s.t.} \quad D_{\mathrm{KL}}(\pi_{\theta_\mathrm{old}} \| \pi_\theta) \leq \delta$$

#### M16: PPO 精读 — Schulman 2017, S-tier (1h)

**Clipped surrogate objective**：用 clip 替代 KL 硬约束

$$L^{\mathrm{CLIP}}(\theta) = \mathbb{E}_t \left[\min\left(r_t(\theta) \hat{A}_t, \; \operatorname{clip}(r_t(\theta), \, 1-\epsilon, \, 1+\epsilon) \hat{A}_t\right)\right]$$

其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_\mathrm{old}}(a_t|s_t)}$ 是概率比

#### M17: 早期 RLHF 验证 — Ziegler 2019 + Stiennon 2020, A-tier (0.5h)

速读。从人类偏好训练 reward model → 用 PPO 优化。验证了"人类反馈 + RL"的可行性

#### M18: InstructGPT 精读 — Ouyang 2022, S-tier (2.5h)

**RLHF 完整 pipeline**（三阶段）：

1. **SFT**：在人类示范数据上微调
2. **Reward Model**：用 Bradley-Terry 模型训练

$$P(y_w \succ y_l \mid x) = \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))$$

$$\mathcal{L}_{\mathrm{RM}} = -\mathbb{E}_{(x, y_w, y_l)}\left[\log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))\right]$$

3. **PPO + KL penalty**：

$$\max_{\pi_\theta} \; \mathbb{E}_{x \sim \mathcal{D}, \, y \sim \pi_\theta(\cdot|x)} \left[r_\phi(x, y)\right] - \beta \, D_{\mathrm{KL}}\left[\pi_\theta(\cdot|x) \,\|\, \pi_{\mathrm{ref}}(\cdot|x)\right]$$

Bradley-Terry 与 Elo 同源：$P(A \succ B) = \sigma(r(A) - r(B))$

#### M19: Helpful & Harmless 精读 — Bai 2022, S-tier (1.25h)

在线迭代 RLHF + safety alignment。每轮：收集偏好 → 训练 RM → PPO → 部署 → 再收集

核心贡献：HH 数据集 + 证明 RLHF 能同时提升 helpfulness 和 harmlessness

#### M20: HuggingFace "Illustrating RLHF" 博客 (0.5h)

理论到工程的桥梁：SFT / RM / PPO 的实际训练流程图

#### M21: Karpathy "Let's build GPT" 视频 (2h)

Self-attention 的每个组件：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V$$

- $Q = XW_Q, \; K = XW_K, \; V = XW_V$
- $\sqrt{d_k}$ 缩放防止 softmax 饱和
- causal mask：上三角置 $-\infty$，确保 token 只看到过去
- Multi-Head：$\text{MultiHead}(Q,K,V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W^O$
- Transformer block：LayerNorm → MHA → residual → LayerNorm → FFN → residual

#### M22: ILF 细读 — Chen 2023 (Scheurer et al.), A-tier (1h)

**初稿 → 自然语言反馈 → 改写 → MLE 微调**

与 RLHF 的区别：不需要 RM，直接用语言反馈指导改写，然后在改写后的好输出上做 supervised fine-tuning

#### M23: Chain-of-Hindsight + Constitutional AI — A-tier (0.75h)

**Chain-of-Hindsight** (Liu 2024)：将正/负反馈编码为序列前缀，让模型学会"如果给了好评/差评，后续应该怎么写"

**Constitutional AI** (Bai 2022)：用 AI 反馈替代人类反馈。模型自我批评 → 自我修正 → RLAIF

#### M24: DPO 预推导 (0.5h)

从 RLHF 的 KL 约束目标出发，尝试推导 closed-form。卡住的地方标注，留给 Day 4

#### M25: GoBeyond 核心代码 — brain.py (1h)

`brain.py` 核心循环：

- `_observe()`：用 vLLM logits 做 support_need / valence / engagement 判别
- `_update_belief()`：prediction_error 驱动 EMA 更新

$$b_{t+1} = (1 - \alpha) \cdot b_t + \alpha \cdot o_t$$

- `_generate()` + `_rerank()`：生成 16 个候选回复，6 维打分后选最优

**核心 insight**：rerank = 不需训练的 reward model（用 LLM logits 直接打分）

#### Day 3 Checklist

- [ ] Policy gradient 公式能默写
- [ ] PPO clipped objective 能解释每一项
- [ ] **能画出 RLHF 完整 pipeline**（SFT → RM → PPO + KL）
- [ ] Bradley-Terry 模型能写出
- [ ] Karpathy 视频看完，self-attention 每步能复述
- [ ] **S 级（InstructGPT + HH）+ A 级前 5 篇（PPO / Ziegler+Stiennon / ILF / CoH / Constitutional AI）全部完成**
- [ ] GoBeyond observe → update → rerank 流程能复述
- [ ] 能说出：GoBeyond rerank ≈ 不需训练的 RM

---

### Day 4 · 5/22 周一 · 10h · DPO 精读 + nanoGPT + Text2Grad

#### M26: DPO 精读 Section 1-4 — Rafailov 2023, S-tier (2h)

**DPO 推导全链路**（每步纸上跟推）：

**Step 1** — RLHF 目标（KL 约束优化）：

$$\max_\pi \; \mathbb{E}_{x, y \sim \pi} [r(x,y)] - \beta \, D_{\mathrm{KL}}[\pi(\cdot|x) \| \pi_{\mathrm{ref}}(\cdot|x)]$$

**Step 2** — closed-form 最优策略：

$$\pi^*(y|x) = \frac{1}{Z(x)} \pi_{\mathrm{ref}}(y|x) \exp\left(\frac{1}{\beta} r(x,y)\right)$$

其中 $Z(x) = \sum_y \pi_{\mathrm{ref}}(y|x) \exp\left(\frac{1}{\beta} r(x,y)\right)$ 是配分函数

**Step 3** — 反解 reward：

$$r(x,y) = \beta \log \frac{\pi^*(y|x)}{\pi_{\mathrm{ref}}(y|x)} + \beta \log Z(x)$$

**Step 4** — 代入 Bradley-Terry，$Z(x)$ 消去：

$$\boxed{L_{\mathrm{DPO}}(\pi_\theta; \pi_{\mathrm{ref}}) = -\mathbb{E}_{(x, y_w, y_l)} \left[\log \sigma\!\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{\mathrm{ref}}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{\mathrm{ref}}(y_l|x)}\right)\right]}$$

DPO vs RLHF：砍掉 RM + 在线采样，直接从偏好数据优化策略。工程更简，但受离线数据质量限制

#### M27: DPO 推导独立重现 (1.5h)

合上论文，白纸推导。目标：< 15 分钟完成全链路

#### M28: DPO Section 5 + PyTorch 伪代码 (0.5h)

实验结果 + DPO 的 PyTorch 实现骨架

#### M29: nanoGPT — Tokenizer + Embedding + PE (1h)

Character-level tokenizer → `nn.Embedding` → positional encoding

$$\text{PE}_{(pos, 2i)} = \sin\!\left(\frac{pos}{10000^{2i/d}}\right), \quad \text{PE}_{(pos, 2i+1)} = \cos\!\left(\frac{pos}{10000^{2i/d}}\right)$$

#### M30: nanoGPT — Self-Attention + Multi-Head + Block (1.5h)

$Q/K/V$ → scaled dot-product → causal mask → FFN → LayerNorm → residual connection

完整 Transformer block 实现

#### M31: nanoGPT — 完整模型 + 训练 + TinyShakespeare (1h)

堆叠 N 层 → cross-entropy loss → AdamW 优化器 → 生成文本

#### M32: nanoGPT 收尾 + push GitHub (1h)

注释、README、确认复现、push

#### M33: Text2Grad + Fine-Grained RLHF — A-tier (1h)

**Text2Grad** (Wang 2025)：将自然语言反馈转为 span 级梯度信号，直接更新模型参数。不需要 RM，反馈粒度比 DPO 更细

**Fine-Grained RLHF** (Wu 2023)：细粒度奖励 — 对输出的每个片段分别打分，而非只给一个整体偏好

**A 级论文全部完成**

#### M34: Goodfellow 注意力 — 12.4.1-12.4.5 (0.75h)

n-gram → 神经语言模型 → **注意力机制**的演化脉络

#### Day 4 Checklist

- [ ] **白纸推导 DPO loss < 15 分钟**
- [ ] **nanoGPT 跑通 + push GitHub**
- [ ] **全部 S+A 级论文完成**
- [ ] Goodfellow 注意力章节完成

---

### Day 5 · 5/23 周二 · 10h · Mini-DPO 全流程 + Memo + CV/邮件

> 关键日：Mini-DPO 跑通 + Memo 初稿 + 邮件。之后两天考试

#### M35: 环境 + 数据准备 (1h)

Anthropic/hh-rlhf 数据集子集（~1000 条偏好对）。编写 `data/prepare.py`

#### M36: SFT Baseline (1.5h)

GPT-2 / SmolLM-135M，手写训练循环（不用 HuggingFace Trainer），保存 checkpoint

#### M37: DPO Loss 实现 (1.25h)

核心函数 `dpo_loss()` 实现：

```python
def dpo_loss(pi_logprobs_w, pi_logprobs_l, ref_logprobs_w, ref_logprobs_l, beta):
    pi_ratio_w = pi_logprobs_w - ref_logprobs_w
    pi_ratio_l = pi_logprobs_l - ref_logprobs_l
    loss = -F.logsigmoid(beta * (pi_ratio_w - pi_ratio_l))
    return loss.mean()
```

关键验证：shift-by-one 对齐（label 向左 shift 一位）、padding mask 正确处理

#### M38: DPO 训练 + Debug (3.5h)

`train_dpo.py`：ref model 冻结 → DPO loss → AdamW → logging

loss 曲线检查：DPO loss 应单调下降；如果不降，debug 路径：
1. `log_prob` 的 shift-by-one bug
2. ref model 是否真正冻结（`requires_grad=False`）
3. $\beta$ 值是否合理（通常 0.1-0.5）
4. 数据质量（chosen/rejected 是否真的有差异）

#### M39: 评测 + GitHub (1h)

SFT vs DPO 对比生成 → loss 曲线图 → push GitHub

#### M40: 技术 Memo 初稿 (1.5h)

3 页核心内容：
1. DPO 推导（1 页）
2. Mini-DPO 实验结果（1 页）
3. 两条路线对比（1 页，含 GoBeyond 简要分析）

5/27 扩充到 4-5 页

#### M41: CV + 邮件终稿 (0.5h)

CV 加上 nanoGPT + Mini-DPO 项目。邮件附 GitHub 链接 + Memo PDF

#### Day 5 Checklist

- [ ] SFT baseline 跑通
- [ ] `dpo_loss()` 实现并通过手算验证
- [ ] **Mini-DPO 跑通 + loss 曲线 + 生成对比**
- [ ] Mini-DPO push GitHub
- [ ] **Memo 初稿完成（3 页）**
- [ ] **CV + 邮件终稿完成**
- [ ] **ALL DELIVERABLES DONE — 安心考试**

---

### Day 6 · 5/24 周三 · 0h · 考试

---

### Day 7 · 5/25 周四 · 0h · 考试

---

### Day 8 · 5/26 周五 · 3h · D-DAY：见教授

> 另有 5h 作业

#### M42: 发邮件 (15min)

Memo PDF + GitHub 链接。9 点前发出

#### M43: 推导 + 问答速过 (1h)

DPO 白纸推导 < 10 分钟 + 10 个面试问题口头过一遍

#### M44: 准备 Demo (0.5h)

nanoGPT 生成演示 / Mini-DPO loss 曲线 / SFT vs DPO 对比结果

#### M45: 材料检查 + 见教授 (1.25h)

材料清单：Memo / GitHub / CV / 电脑 / 手写推导本

见教授流程：自我介绍 → 递交 Memo → 问项目期望 → 展示代码/推导 → 记录反馈

#### Day 8 Checklist

- [ ] **邮件已发送**（9 点前）
- [ ] **教授已见面**
- [ ] 记录教授反馈要点

---

### Day 9 · 5/27 周六 · 10h · GoBeyond 深入 + TRL + Goodfellow 补遗 + Memo 扩充

> 阶段二开始：见完教授后深度补强

#### M46: 消化教授反馈 (1h)

他强调了什么？面试重点调整？需要补什么？调整后续策略

#### M47: GoBeyond 深入 — prompts.py (1h)

`render_context()` 如何组装 system prompt：persona + scene guidance + belief/value 注入 + memory retrieval

#### M48: GoBeyond 深入 — storage.py + vllm.py (1h)

- `storage.py`：SQLite 持久化 belief / dialogue / memory
- `vllm.py`：`/generative_scoring` 接口替代独立 RM — 直接用 LLM 自身的 logits 做评分

#### M49: GoBeyond 深入 — eval/ + experiment.py (1h)

灰测框架：scenario → transcript → score → compare

experiment profile：怎么调参（persona 权重、belief 衰减率等）

#### M50: TRL 上手 — SFTTrainer + DPOTrainer (2h)

各跑一遍标准流程，对比工业级工具链 vs 手写实现的差异

#### M51: TRL 源码阅读 (1h)

DPOTrainer 源码 vs 手写的 `dpo_loss()` 逐行对比。重点关注：
- label smoothing
- reference model 管理
- length normalization
- loss 类型变体（sigmoid / hinge / IPO）

#### M52: Goodfellow 补遗 — Ch 5, 7, 8 (1h)

- 7.1.1 L2 正则（权重衰减）：$\tilde{J}(\theta) = J(\theta) + \frac{\alpha}{2} \|\theta\|_2^2$
- 7.5 噪声鲁棒性
- 7.8 提前终止
- 5.10-5.11 ML 算法构建 + DL 面临的挑战
- 8.7.1 批标准化（Batch Normalization）

#### M53: Memo 扩充到 4-5 页 (1.5h)

新增内容：
- GoBeyond 系统分析（1 页）
- 参数 vs 非参数对比
- 融合可能性（GoBeyond eval 评测 DPO / DPO 模型替换 base model / belief 信号做在线数据采集）
- DPO 踩坑笔记

#### M54: 手写对比笔记 (0.5h)

GoBeyond（非参数）vs Mini-DPO（参数）：

| 维度 | Mini-DPO（参数） | GoBeyond（非参数） |
|------|------------------|---------------------|
| 学习方式 | 改权重 $\theta$ | 改 state / memory / prompt |
| 更新信号 | 偏好对 $(y_w, y_l)$ | prediction error（实时观测） |
| 泛化性 | 强（编码进权重） | 弱（依赖检索 + prompt） |
| 即时适应 | 弱（需重新训练） | 强（每轮对话即时更新） |
| 可解释性 | 低（黑箱权重） | 高（belief state 可读） |
| reward 来源 | 显式 RM 或 DPO 隐式 | LLM logits 多维打分（rerank） |

observe / reward / update 对应关系 + tradeoff 分析

#### Day 9 Checklist

- [ ] GoBeyond prompts + storage + vllm + eval 全部读完
- [ ] **参数 vs 非参数对比笔记完成**
- [ ] TRL 跑通 + 源码 vs 手写代码对比完成
- [ ] Goodfellow 补遗完成
- [ ] **Memo 扩充到 4-5 页**

---

### Day 10 · 5/28 周日 · 10h · B 级论文 + 改进实验 + 模拟面试 + 全面打磨

#### M55: B 级论文略读 × 6 (1h)

每篇 ~10min，掌握核心定位：

| 论文 | 核心 |
|------|------|
| LLF-Bench | 语言反馈学习的 benchmark |
| LifelongAgentBench | 终身学习 agent 评测 |
| MT-Bench | 多轮对话评测（GPT-4 作为 judge） |
| AlpacaEval | 自动评测 LLM 指令遵循 |
| TruthfulQA | 测试模型是否生成真实信息 |
| HELM | 多维度大模型评测框架 |

#### M56: C 级论文补读 (1h)

- **OpenRLHF**：开源 RLHF 训练框架，工程参考
- **GPT-4 System Card**：safety alignment 的工业实践

#### M57: Mini-DPO 改进实验 (1h)

不同 $\beta$ 值的实验：$\beta \in \{0.05, 0.1, 0.2, 0.5\}$

画图对比 loss 曲线 + 生成质量 → 更新 Memo

$\beta$ 的直觉：越大 → 越保守（越靠近 $\pi_{\mathrm{ref}}$），越小 → 越激进（更容易 reward hack）

#### M58: Goodfellow 收尾 — Ch 10 (2h)

- 10.1-10.4 序列建模：RNN、teacher forcing、双向 RNN、encoder-decoder
- 10.7 长期依赖问题：梯度消失/爆炸 → LSTM / GRU 的动机

#### M59: Memo 终稿润色 → 导出 PDF (1.5h)

#### M60: GitHub repo 最终打磨 (0.5h)

#### M61: 全真模拟面试 × 2 轮 (2h)

第 1 轮：技术问答（12 问）
第 2 轮：项目理解 + 反问

#### M62: 薄弱环节补强 (1h)

根据模拟面试暴露的问题针对性复习

#### Day 10 Checklist

- [ ] B + C 级论文全部完成
- [ ] Mini-DPO $\beta$ 实验完成
- [ ] **Goodfellow 全书必读章节 100% 完成**
- [ ] **Memo 终稿 PDF 导出**
- [ ] GitHub 最终打磨
- [ ] 模拟面试 × 2 完成

---

### Day 11 · 5/29 周一 · 4h · 面试最终准备

#### M63: 所有推导再过一遍 (1h)

- DPO loss 全链路
- Policy Gradient（REINFORCE + baseline）
- Bellman 方程（期望 + 最优）
- $D_{\mathrm{KL}} \geq 0$（Jensen 不等式）

#### M64: 面试问答精炼 (1h)

12 个问题每个 2 分钟。录音回听，优化表达

#### M65: 概念卡片制作 (0.75h)

每张卡片一个核心概念，正面问题反面答案

#### M66: 设备检查 + 反问清单最终版 (0.75h)

笔记本能跑 Demo / Memo PDF / GitHub / 手写推导本

#### M67: 放松 (0.5h)

做完了。明天的你已经准备好了

#### Day 11 Checklist

- [ ] 推导全部过一遍
- [ ] 面试问答精炼完成
- [ ] 设备检查完毕
- [ ] **准备完毕，明天面试**

---

### Day 12 · 5/30 周二 · 面试日

上午：轻松复习概念卡片（1h）。不要临阵学新东西

下午：**面试**

---

## Exams

### 面试 12 问

> 每个准备 2 分钟回答

1. **RLHF 完整 pipeline？** → SFT → RM（Bradley-Terry）→ PPO + KL penalty，画图
2. **DPO vs RLHF？** → 砍掉 RM + 在线采样，closed-form，工程更简，但受离线数据质量限制
3. **KL 散度的作用？** → 弹簧比喻：$\beta D_{\mathrm{KL}}[\pi_\theta \| \pi_{\mathrm{ref}}]$ 防止 reward hacking
4. **语言反馈 vs 偏好反馈？** → 信息密度递增：1 bit → 偏好对 → 定位 + 类型 + 原因
5. **哪条路线最有潜力？** → 你的判断 + 理由
6. **Self-attention？** → $QK^\top / \sqrt{d_k}$ → softmax → 加权 $V$，causal mask
7. **Bradley-Terry？** → $P(A \succ B) = \sigma(r(A) - r(B))$，和 Elo 同源
8. **参数 vs 非参数在线学习？** → Mini-DPO = 改权重，GoBeyond = 改 state/memory/prompt。泛化性 vs 即时适应 vs 可解释性
9. **DPO loss 不降怎么 debug？** → log_prob shift bug → ref 冻结 → $\beta$ → 数据质量
10. **GoBeyond 的 rerank 和 RM 的关系？** → logits 多维打分 = 不需训练的 RM；但不能泛化新场景
11. **两条路线怎么融合？** → GoBeyond eval 评测 DPO / DPO 模型替换 base model / belief 信号做在线 DPO 数据采集
12. **你能贡献什么？** → 展示 Mini-DPO repo + GoBeyond 分析笔记，说具体任务

### 反问清单

1. 项目目前进展到哪一步了？我加入后第一个任务会是什么？
2. 算力怎么安排？我能用多大的模型做实验？
3. 三条路线里，您更倾向先推进哪条？
4. GoBeyond 的非参数路线和参数微调路线，有计划做融合实验吗？
5. 对我这个阶段的学生，您的期望和培养计划是什么？

---

## Progress Tracker

### Goodfellow 章节

| 章节 | 内容 | Day | 完成 |
|------|------|-----|------|
| 2.1-2.5 | 线代基础 + 范数 | 1 | [ ] |
| 3.1-3.5 | 概率基础 | 1 | [ ] |
| 3.10-3.11 | 常用函数 + 贝叶斯 | 1 | [ ] |
| 3.13 | 信息论 / KL 散度 | 1 | [ ] |
| 3.6-3.9 | 概率深入 | 2 | [ ] |
| 4.3-4.4 | 梯度优化 + 约束优化 | 2 | [ ] |
| 5.1-5.2 | 学习框架 + 容量 | 2 | [ ] |
| 5.4-5.5 | 偏差方差 + MLE | 2 | [ ] |
| 5.6-5.7 + 5.9 | MAP + 监督 + SGD | 2 | [ ] |
| 6.1-6.4 | 神经网络基础 | 2 | [ ] |
| 6.2.1-6.2.2 | 代价函数 + softmax | 2 | [ ] |
| 6.5.1-6.5.3 | 反向传播 | 2 | [ ] |
| 8.1 + 8.3 + 8.5 | 优化器 | 2 | [ ] |
| 12.4.1-12.4.5 | NLP + 注意力 | 4 | [ ] |
| 7.1.1 + 7.5 + 7.8 | L2 正则 + 噪声鲁棒 + 提前终止 | 9 | [ ] |
| 5.10-5.11 | ML 算法构建 + DL 挑战 | 9 | [ ] |
| 8.7.1 | 批标准化 | 9 | [ ] |
| 10.1-10.4 + 10.7 | 序列建模 + 长期依赖 | 10 | [ ] |

### 论文

| 级别 | 论文 | Day | 完成 |
|------|------|-----|------|
| S | InstructGPT (Ouyang 2022) | 3 | [ ] |
| S | DPO (Rafailov 2023) | 4 | [ ] |
| S | HH Assistant (Bai 2022) | 3 | [ ] |
| A | PPO (Schulman 2017) | 3 | [ ] |
| A | Ziegler 2019 + Stiennon 2020 | 3 | [ ] |
| A | ILF (Scheurer / Chen 2023) | 3 | [ ] |
| A | Chain-of-Hindsight (Liu 2024) | 3 | [ ] |
| A | Constitutional AI (Bai 2022) | 3 | [ ] |
| A | Text2Grad (Wang 2025) | 4 | [ ] |
| A | Fine-Grained RLHF (Wu 2023) | 4 | [ ] |
| B | LLF-Bench / LifelongAgentBench / MT-Bench / AlpacaEval / TruthfulQA / HELM | 10 | [ ] |
| C | OpenRLHF / GPT-4 System Card | 10 | [ ] |

### GoBeyond 学习

| 模块 | Day | 完成 |
|------|-----|------|
| README + models.py（架构 + 数据结构） | 2 | [ ] |
| brain.py 核心循环（observe / update / rerank） | 3 | [ ] |
| prompts.py（context 组装） | 9 | [ ] |
| storage.py + vllm.py（持久化 + logits 接口） | 9 | [ ] |
| eval/ + experiment.py（灰测框架） | 9 | [ ] |
| 参数 vs 非参数对比笔记 | 9 | [ ] |

### Deliverables

| 产出 | Deadline | 完成 |
|------|----------|------|
| nanoGPT 跑通 + push GitHub | Day 4 (5/22) | [ ] |
| Mini-DPO: SFT + DPO + 评测 + push | Day 5 (5/23) | [ ] |
| Memo 初稿（3 页） | Day 5 (5/23) | [ ] |
| CV + 邮件终稿 | Day 5 (5/23) | [ ] |
| 邮件发送 | Day 8 (5/26) | [ ] |
| 见教授 | Day 8 (5/26) | [ ] |
| Memo 终稿（4-5 页，含 GoBeyond） | Day 10 (5/28) | [ ] |
| 面试 | Day 12 (5/30) | [ ] |
