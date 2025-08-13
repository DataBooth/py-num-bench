import pytest
from py_num_bench.implementations.python.sieve import sieve_py


@pytest.mark.parametrize(
    "n,expected",
    [
        (10, [2, 3, 5, 7]),
        (2, [2]),
        (1, []),
    ],
)
def test_python_sieve_basic(n, expected):
    assert sieve_py(n) == expected
