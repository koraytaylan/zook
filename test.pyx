#!python
#cython: boundscheck=False, wraparound=False, cdivision=True
cimport cython

cdef class Rectangle:
    cdef int x0, y0
    cdef int x1, y1
    def __init__(self, int x0, int y0, int x1, int y1):
        self.x0 = x0; self.y0 = y0; self.x1 = x1; self.y1 = y1
    cdef int _area(self):
        cdef int area
        area = (self.x1 - self.x0) * (self.y1 - self.y0)
        if area < 0:
            area = -area
        return area
    def area(self):
        return self._area()

    def rectArea(self, x0, y0, x1, y1):
        cdef Rectangle rect
        rect = Rectangle(x0, y0, x1, y1)
        return rect._area()

    cdef double test(self, ):
        cdef long double x = 1.2
        cdef long double y = 0.1
        z = round(x)
        z = round(x, 5)
        return x - y

    cdef double roundup(self, double x, double y):
        h = y
        cdef double z
        if x > y:
            for i in range(2, 100):
                j = round(y, 5)
                z = i * y
                if x <= z:
                    return round(z, 5)
        if x < h:
            return round(h, 5)
        if x == h:
            return round(h, 5)