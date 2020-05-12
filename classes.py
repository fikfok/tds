class Point:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def __add__(self, other_point):
        return Point(x=self._x + other_point._x, y=self._y + other_point._y)

    def __repr__(self):
        return 'Point(x={x}, y={y})'.format(x=self._x, y=self._y)


point1 = Point(x=1, y=1)
point2 = Point(x=2, y=2)
point4 = point1 + point2

print(point1)
print(point2)
print(point4)


