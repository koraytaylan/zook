def subtract(x, y):
    return x - y


def roundup(x, y):
    h = y
    if x > y:
        for i in range(2, 100):
            z = i * round(y, 5)
            if x <= z:
                return round(z, 5)
    if x < h:
        return round(h, 5)
    if x == h:
        return round(h, 5)