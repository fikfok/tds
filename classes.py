class GlobalClass:

    def __init__(self, x, y=None):
        self.x = x
        self.y = y

    def __eq__(self, other):
        print("eq")
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        return self.x < other.x and self.y < other.y

    def __le__(self, other):
        return self.x <= other.x and self.y <= other.y

    def __gt__(self, other):
        return self.x > other.y and self.y > other.y


a = GlobalClass(5, 6)
b = GlobalClass(5, 8)
c = a == b
print(c)
print(a < b)
print(a > b)
print(a <= b)
print(2 < 3 < 4)



