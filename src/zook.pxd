import cython

@cython.locals(t = cython.int, i = cython.int)
cpdef double dostuff(int n)