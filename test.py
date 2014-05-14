import copy

class A:
    def __init__(self):
        self.a = 0
        self.b = 1

class B:
    def __init__(self):
        self.d = {0: A(), 1: A()}

b = B()
d = copy.copy(b.__dict__)
d['d'] = copy.copy(d['d'])
d['d'][0] = d['d'][0].__dict__
b.d
