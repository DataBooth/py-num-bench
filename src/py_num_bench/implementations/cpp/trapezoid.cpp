// trapezoid.cpp
// Naive trapezoidal integration of f(x) = x^2 over [a,b] (exposed via pybind11 - https://pybind11.readthedocs.io)

#include <cmath>

extern "C" double trapezoid_cpp(double a, double b, int n) {
    double h = (b - a) / n;
    double s = 0.5 * (a * a + b * b);

    for (int i = 1; i < n; i++) {
        double x = a + i * h;
        s += x * x;  // f(x) = x^2
    }
    return s * h;
}

