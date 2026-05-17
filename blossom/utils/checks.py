"""学生填空自动验证模块。

每个填空 cell 后调用 assert_*，学生看到 ✅ 或 ❌ + 友好提示。
封装为函数（而非裸 assert）让错误信息更清晰，且不中断 notebook 执行。
"""

import numpy as np


def _ok(name):
    print(f"✅ {name} 通过")


def _fail(name, msg):
    print(f"❌ {name} 失败：{msg}")
    print("   提示：检查上方填空 / 回看 Sec 1-5 的解释 / 必要时重启 kernel 全跑")


def assert_equal(name, student, expected, tol=1e-8):
    """检查学生答案与期望值相等（支持 numpy array、浮点标量、整数/字符串/tuple）。"""
    try:
        if isinstance(expected, np.ndarray) or isinstance(student, np.ndarray):
            student_arr = np.asarray(student)
            expected_arr = np.asarray(expected)
            if student_arr.shape != expected_arr.shape:
                _fail(name, f"形状不匹配：你给的 {student_arr.shape}，期望 {expected_arr.shape}")
                return
            if not np.allclose(student_arr, expected_arr, atol=tol):
                _fail(name, f"数值不匹配（容差 {tol}）\n你给的：\n{student_arr}\n期望：\n{expected_arr}")
                return
        elif isinstance(expected, (float, np.floating)) or isinstance(student, (float, np.floating)):
            if not np.isclose(float(student), float(expected), atol=tol):
                _fail(name, f"你给的 {student!r}，期望 {expected!r}（容差 {tol}）")
                return
        else:
            if student != expected:
                _fail(name, f"你给的 {student!r}，期望 {expected!r}")
                return
    except Exception as e:
        _fail(name, f"比对时抛异常：{e}")
        return
    _ok(name)


def assert_shape(name, arr, expected_shape):
    """检查数组形状。"""
    try:
        arr = np.asarray(arr)
    except Exception as e:
        _fail(name, f"无法转 ndarray：{e}")
        return
    if arr.shape != expected_shape:
        _fail(name, f"形状不对：实际 {arr.shape}，期望 {expected_shape}")
        return
    _ok(name)


def assert_close(name, student, expected, tol=1e-6):
    """assert_equal 的别名，专用于浮点比较。"""
    assert_equal(name, student, expected, tol=tol)


def assert_true(name, condition, hint=""):
    """检查一个布尔条件成立。"""
    if not condition:
        _fail(name, f"条件不成立。{hint}")
        return
    _ok(name)


def report():
    """章末提示。"""
    print("=" * 40)
    print("本章自检走完。回头看上面所有断言：")
    print("- 全 ✅ 表示填空正确")
    print("- 出现 ❌ 请回到对应 Sec 修正再重跑这一格")
    print("=" * 40)
