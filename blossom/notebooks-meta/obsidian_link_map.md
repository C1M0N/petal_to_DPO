# notebook ↔ vault notio 双向索引

记录每个 notebook 引用了哪些 Cementine Vault 的 notio。
反过来 vault 那 5 个 notio 的"配套 notebook"小节回链到这里的对应 notebook。

## Vault 路径

Cementine Vault 根：`/Users/lainos/Dropbox/Ptolemaeus Studio/Cementine Vault`

Notio 都在 `30 The Colonnade/` 下。

## Ch 2：线性代数

| Notebook 引用位置 | Vault Notio | Vault 路径 |
|------------------|------------|-----------|
| Sec 1.E3、Sec 2、Sec 3.4 | [张量] | `30 The Colonnade/张量.md` |
| Sec 3.4、Sec 6.E1、Sec 6.E8 | [矩阵乘法] | `30 The Colonnade/矩阵乘法.md` |
| Sec 3.3、Sec 6（多处对比） | [Hadamard 乘积] | `30 The Colonnade/Hadamard 乘积.md` |
| Sec 3.6 简写、Sec 6.E8 | [Einstein 求和约定] | `30 The Colonnade/Einstein 求和约定.md` |
| Sec 5 概念地图 | [张量语言] | `30 The Colonnade/张量语言.md` |

## URI 用法

notebook 里通过 obsidian URI 链接（点击在 Obsidian 中打开）：

```markdown
[张量](obsidian://open?vault=Cementine%20Vault&file=30%20The%20Colonnade%2F%E5%BC%A0%E9%87%8F)
```

URL 编码要点：
- `Cementine Vault` → `Cementine%20Vault`
- `/` → `%2F`
- 中文字符按 UTF-8 编码为 `%XX%XX...`

## 反向链接（vault 侧应有的"配套 notebook"行）

每个上面 5 个 notio 的"## 相关"节末尾应该有一行：

```markdown
> 配套 notebook：`Turner Sienter/petal_to_DPO/blossom/ch02-linear-algebra/ch02.ipynb`
```

后续添加 Ch 3+ 时同步更新这张表。
