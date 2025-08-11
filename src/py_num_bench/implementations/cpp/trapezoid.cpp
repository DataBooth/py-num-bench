// trapezoid.cpp
// Naive trapezoidal integration of f(x) = x^2 over [a,b] (exposed via pybind11 - https://pybind11.readthedocs.io)

#include <pybind11/pybind11.h>

namespace py = pybind11;

double trapezoid_cpp(double a, double b, int n) {
    double h = (b - a) / n;
    double s = 0.5 * (a*a + b*b);
    for (int i = 1; i < n; ++i) {
        double x = a + i*h;
        s += x*x;
    }
    return s * h;
}

PYBIND11_MODULE(trapezoid_cpp, m) {
    m.def("trapezoid_cpp", &trapezoid_cpp);
}
