#include <stdio.h>

int main(void)
{
    float aboat = 32000.0;
    double abet = 5.32e-5;
    long double dip = 5.32e-5;

    printf("%f can be written %e\n", aboat, aboat);
    printf("%f can be written %e\n", abet, abet);
    printf("%lf can be written %le\n", dip, dip);

    double x = 1.2;
    double y = 0.1;
    double z = x - y;

    printf("%f", z);

    return 0;
}