import os
from setuptools import setup, Extension
from Cython.Build import cythonize

this_dir = os.path.dirname(os.path.abspath(__file__))

extensions = [
    Extension("sieve_cython", [os.path.join(this_dir, "sieve_cython.pyx")]),
    Extension("trapezoid_cython", [os.path.join(this_dir, "trapezoid_cython.pyx")]),
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}),
)
