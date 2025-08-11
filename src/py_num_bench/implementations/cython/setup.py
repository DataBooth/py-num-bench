from Cython.Build import cythonize
from setuptools import setup

setup(
    name="py_num_bench_cython_extensions",
    ext_modules=cythonize(["sieve_cython.pyx", "trapezoid_cython.pyx"]),
    zip_safe=False,
)
