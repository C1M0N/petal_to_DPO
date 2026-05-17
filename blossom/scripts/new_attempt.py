#!/usr/bin/env python3
"""开始/继续一份可写的章节学习副本（attempt），并自动在 VS Code 里打开。

build.py 生成的 ch{NN}.ipynb（demo）和 ch{NN}_work.ipynb（work）是**只读**的
——它们是「教材副本」，不在上面做题。本脚本帮你**复制一份可写副本**来做。

最常用：
    python3 scripts/new_attempt.py ch02
        → 如果 ch02_attempt.ipynb 已存在：直接在 VS Code 里打开它
        → 如果不存在：基于 ch02_work 复制一份 + 在 VS Code 里打开
    或者用根目录 wrapper：
        ./start ch02

重做一遍（覆盖现有进度）：
    python3 scripts/new_attempt.py ch02 -f
    ./start ch02 -f

复习（基于 demo 含答案的副本）：
    python3 scripts/new_attempt.py ch02 --from-demo --name review
    ./start ch02 -d -n review

不自动打开 VS Code：
    python3 scripts/new_attempt.py ch02 --no-open
"""

import argparse
import os
import platform
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
IS_MACOS = platform.system() == "Darwin"


def _unlock_macos(path: Path):
    """macOS: 移除 user-immutable 标志，让文件可写。"""
    if IS_MACOS:
        subprocess.run(["chflags", "nouchg", str(path)], check=False)


def find_chapter_dir(ch: str) -> Path:
    """根据 ch02 → ch02-linear-algebra/ 这种映射找章节目录。"""
    candidates = list(ROOT.glob(f"{ch}-*"))
    if not candidates:
        sys.exit(f"❌ 找不到章节目录 {ch}-* （在 {ROOT}/ 下）")
    if len(candidates) > 1:
        sys.exit(f"❌ 多个匹配目录：{[c.name for c in candidates]}，请手动指定")
    return candidates[0]


def _open_in_vscode(path: Path) -> bool:
    """尝试在 VS Code 里打开。优先 `code` CLI，回退到 macOS `open -a`。"""
    # 1) 优先 code CLI（如果用户装了 VS Code shell command）
    try:
        result = subprocess.run(
            ["code", str(path)],
            check=False, capture_output=True, timeout=10,
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # 2) macOS 回退：用系统 open 命令调起 VS Code app
    if IS_MACOS:
        try:
            result = subprocess.run(
                ["open", "-a", "Visual Studio Code", str(path)],
                check=False, capture_output=True, timeout=10,
            )
            if result.returncode == 0:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

    return False


def main():
    parser = argparse.ArgumentParser(
        description="开始/继续章节学习副本，并自动在 VS Code 里打开",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("ch", help="章节标识，如 ch02、ch03")
    parser.add_argument("-n", "--name", default="attempt",
                        help="副本名后缀（默认 attempt，生成 ch{NN}_attempt.ipynb）")
    parser.add_argument("-d", "--from-demo", action="store_true",
                        help="基于 demo 副本（含答案）而不是 work 副本——复习用")
    parser.add_argument("-f", "--force", action="store_true",
                        help="若目标已存在，强制覆盖重做（默认是直接打开已有副本）")
    parser.add_argument("--no-open", action="store_true",
                        help="不自动在 VS Code 里打开")
    args = parser.parse_args()

    chdir = find_chapter_dir(args.ch)
    src_name = f"{args.ch}.ipynb" if args.from_demo else f"{args.ch}_work.ipynb"
    src = chdir / src_name
    dst = chdir / f"{args.ch}_{args.name}.ipynb"

    # 已存在且没 -f → 直接打开，不复制
    if dst.exists() and not args.force:
        print(f"📓 已有可写副本：{dst.relative_to(ROOT)}")
        print(f"  （要重做就加 -f；要看 demo 答案就加 -d --name review）")
        if not args.no_open and _open_in_vscode(dst):
            print(f"✅ 已用 VS Code 打开\n")
        elif not args.no_open:
            print(f"⚠️ 未检测到 `code` 命令（VS Code CLI）——请手动在 VS Code 里打开\n")
        _print_kernel_tip()
        return

    if not src.exists():
        sys.exit(f"❌ 源文件不存在：{src.relative_to(ROOT)}\n"
                 f"   先跑 `python3 scripts/build.py` 生成？")

    # 若目标已存在（force 覆盖路径），先解锁
    if dst.exists():
        _unlock_macos(dst)
        os.chmod(dst, stat.S_IWUSR | stat.S_IRUSR)

    # 复制并设为可写（shutil.copy 不会带过 uchg flag，但权限继承源 → 强制 644）
    shutil.copy(src, dst)
    _unlock_macos(dst)  # 兜底再解一次
    os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)  # 0o644

    base_label = "demo（含答案）" if args.from_demo else "work（填空版）"
    print(f"✅ 已基于 {base_label} 复制：{dst.relative_to(ROOT)} [可写]")

    if not args.no_open:
        if _open_in_vscode(dst):
            print(f"✅ 已用 VS Code 打开\n")
        else:
            print(f"⚠️ 未检测到 `code` 命令——请手动在 VS Code 里打开\n")
    _print_kernel_tip()


def _print_kernel_tip():
    print("💡 第一次打开时记得：")
    print("   1. VS Code 右上角「选择内核 / Select Kernel」")
    print("      → 选 `.venv/bin/python` 或显示「blossom (3.11.x)」的那个")
    print("   2. 从顶部顺序读，遇到 📖 看花书原文，遇到 ✏️ 例题就动手填 `___`")
    print("   3. 跑 cell 看 ✅ / ❌ 反馈；CHECKPOINT 全勾完就过关")


if __name__ == "__main__":
    main()
