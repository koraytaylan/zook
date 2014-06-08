from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(
    cmdclass = {'build_ext': build_ext},
    ext_modules = [
        Extension("zook", ["src/zook.py"]),
        Extension("handlers", ["src/handlers.py"]),
        Extension("test", ["test.pyx"])
    ]
)