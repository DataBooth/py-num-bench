"""
Naive pure Python trapezoidal rule integration of f(x) = x^2 over [a,b].
"""


def trapezoid_py(a: float, b: float, n: int):
    h = (b - a) / n
    s = 0.5 * (a * a + b * b)
    for i in range(1, n):
        x = a + i * h
        s += x * x
    return s * h
