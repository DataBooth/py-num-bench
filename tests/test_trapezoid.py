import pytest
from py_num_bench.implementations.python.trapezoid import trapezoid_py


def test_python_trapezoid_exact():
    # Analytical integral of x^2 from 0 to 1 is 1/3 ≈ 0.3333...
    approx = trapezoid_py(0.0, 1.0, 100000)
    assert abs(approx - 1.0 / 3.0) < 1e-10
