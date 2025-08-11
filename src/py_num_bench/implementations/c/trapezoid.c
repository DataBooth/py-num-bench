/* trapezoid.c
   Naive trapezoidal integration of f(x) = x^2 over [a,b].
   Arguments:
     a, b : integration limits
     n    : number of subintervals
   Returns:
     approximate integral value as double
*/

double trapezoid(double a, double b, int n) {
    double h = (b - a) / n;
    double s = 0.5 * (a*a + b*b);
    for (int i = 1; i < n; ++i) {
        double x = a + i*h;
        s += x*x;
    }
    return s * h;
}
