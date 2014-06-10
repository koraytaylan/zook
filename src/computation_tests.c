#include <glib.h>
 
void computationTest(void)
{
    g_assert_cmpint(1234, ==, 1);
}
 
int main(int argc, char** argv)
{
    g_test_init(&argc, &argv, NULL);
    g_test_add_func("/package_name/unit", computationTest);
    return g_test_run();
}