# trapezoid_cython.pyx

"""
Cython naive trapezoidal integration for f(x) = x^2 over [a,b].
"""

def trapezoid_cython(double a, double b, int n):
    cdef double h = (b - a) / n
    cdef double s = 0.5 * (a*a + b*b)
    cdef int i
    cdef double x  # Declare x here, before the loop
    for i in range(1, n):
        x = a + i * h
        s += x * x
    return s * h

