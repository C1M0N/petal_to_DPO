"""matplotlib 可视化 helper，章节复用。

约定：所有函数返回 (fig, ax)；不主动 plt.show()，让 Jupyter inline 自动渲染。
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 中文字体兜底（macOS / Linux 常见）；如系统无对应字体则保持默认
for f in ["PingFang SC", "Heiti SC", "Noto Sans CJK SC", "Microsoft YaHei", "SimHei"]:
    try:
        matplotlib.rcParams["font.sans-serif"] = [f, "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False
        break
    except Exception:
        continue


def plot_vectors(vectors, labels=None, ax=None, colors=None, title=None, lim=None):
    """在 2D 平面上画一组从原点出发的向量。

    vectors: shape (N, 2) 或 list of (2,) arrays
    labels: 每个向量的标签
    """
    vectors = np.asarray(vectors)
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))
    else:
        fig = ax.figure
    if colors is None:
        colors = plt.cm.tab10(np.linspace(0, 1, max(len(vectors), 2)))
    for i, v in enumerate(vectors):
        label = labels[i] if labels else None
        ax.quiver(0, 0, v[0], v[1],
                  angles='xy', scale_units='xy', scale=1,
                  color=colors[i], label=label, width=0.008)
    if lim is None:
        lim = max(float(np.abs(vectors).max()) * 1.3, 1.0)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_aspect('equal')
    ax.grid(alpha=0.3)
    if labels:
        ax.legend()
    if title:
        ax.set_title(title)
    return fig, ax


def plot_matrix_action(A, n_samples=60, ax=None, title=None):
    """画 2x2 矩阵 A 把单位圆变成的椭圆（直观看矩阵作为线性变换）。"""
    A = np.asarray(A, dtype=float)
    assert A.shape == (2, 2), "plot_matrix_action 只支持 2x2 矩阵"
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = ax.figure
    theta = np.linspace(0, 2 * np.pi, n_samples)
    circle = np.stack([np.cos(theta), np.sin(theta)])  # (2, n)
    transformed = A @ circle
    ax.plot(circle[0], circle[1], '--', label='原单位圆', alpha=0.5, color='gray')
    ax.plot(transformed[0], transformed[1], '-', label='A 作用后', lw=2, color='C0')
    # 原基向量
    ax.quiver(0, 0, 1, 0, angles='xy', scale_units='xy', scale=1,
              color='gray', width=0.005, alpha=0.4)
    ax.quiver(0, 0, 0, 1, angles='xy', scale_units='xy', scale=1,
              color='gray', width=0.005, alpha=0.4)
    # A 作用后的基向量（A 的两列）
    ax.quiver(0, 0, A[0, 0], A[1, 0], angles='xy', scale_units='xy', scale=1,
              color='C1', width=0.009, label=r'$A\mathbf{e}_1$')
    ax.quiver(0, 0, A[0, 1], A[1, 1], angles='xy', scale_units='xy', scale=1,
              color='C2', width=0.009, label=r'$A\mathbf{e}_2$')
    lim = max(float(np.abs(transformed).max()), 1) * 1.3
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.grid(alpha=0.3)
    if title:
        ax.set_title(title)
    return fig, ax


def plot_eigen(A, ax=None, title=None):
    """画 2x2 对称矩阵 A 的椭圆 + 特征向量（红色箭头长度 = 特征值绝对值）。"""
    A = np.asarray(A, dtype=float)
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = ax.figure
    plot_matrix_action(A, ax=ax, title=title)
    eigvals, eigvecs = np.linalg.eig(A)
    for i in range(len(eigvals)):
        v = eigvecs[:, i].real * eigvals[i].real
        ax.quiver(0, 0, v[0], v[1], angles='xy', scale_units='xy', scale=1,
                  color='red', width=0.013, alpha=0.85,
                  label=f'特征 λ={eigvals[i].real:.2f}')
    ax.legend(loc='upper right', fontsize=8)
    return fig, ax


def plot_tensor_slices(T, axis=0, max_slices=6, title=None, cmap='viridis'):
    """3 阶张量沿某轴拆成多个 2D 切片并排显示，让"摞起来"具象。"""
    T = np.asarray(T)
    assert T.ndim == 3, "plot_tensor_slices 只支持 3 阶张量"
    T_moved = np.moveaxis(T, axis, 0)
    n = min(T_moved.shape[0], max_slices)
    fig, axes = plt.subplots(1, n, figsize=(2.6 * n, 2.8))
    if n == 1:
        axes = [axes]
    vmin, vmax = float(T_moved.min()), float(T_moved.max())
    for i in range(n):
        im = axes[i].imshow(T_moved[i], vmin=vmin, vmax=vmax, cmap=cmap)
        axes[i].set_title(f"slice [axis={axis}, idx={i}]", fontsize=9)
        axes[i].set_xticks([])
        axes[i].set_yticks([])
    fig.colorbar(im, ax=axes, fraction=0.02, shrink=0.8)
    if title:
        fig.suptitle(title)
    return fig, axes


def plot_points_2d(points, ax=None, c=None, s=20, title=None, label=None):
    """画一组 2D 点（PCA / 数据集可视化用）。"""
    points = np.asarray(points)
    assert points.shape[-1] == 2, "需要 (N, 2) 形状"
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 5))
    else:
        fig = ax.figure
    ax.scatter(points[:, 0], points[:, 1], c=c, s=s, alpha=0.7,
               edgecolors='white', linewidths=0.5, label=label)
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='gray', lw=0.5)
    ax.set_aspect('equal')
    ax.grid(alpha=0.3)
    if title:
        ax.set_title(title)
    if label:
        ax.legend()
    return fig, ax
