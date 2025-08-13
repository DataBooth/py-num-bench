import ctypes
import sys
from pathlib import Path

import pytest


def get_ext():
    if sys.platform == "darwin":
        return ".so"
    elif sys.platform == "win32":
        return ".dll"
    else:
        return ".so"


@pytest.fixture(scope="module")
def sieve_c():
    path = (
        Path().cwd()
        / "src"
        / "py_num_bench"
        / "implementations"
        / "c"
        / f"libsieve{get_ext()}"
    )
    lib = ctypes.CDLL(str(path))
    func = lib.sieve
    func.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
    func.restype = ctypes.c_int

    def wrapper(n):
        arr = (ctypes.c_int * (n + 1))()
        count = func(n, arr)
        return [arr[i] for i in range(count)]

    return wrapper


def test_c_sieve(sieve_c):
    assert sieve_c(10) == [2, 3, 5, 7]
    assert sieve_c(2) == [2]
    assert sieve_c(1) == []
