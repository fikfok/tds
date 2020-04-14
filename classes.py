class Point:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def __le__(self):
        return True


p1 = Point(x=1, y=1)
p1.foo()