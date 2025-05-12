

class car():
    colour = "black"

    def __init__(self, colour, clsColour=None):
        self.colour = colour
        if clsColour:
            car.colour = clsColour

    @classmethod
    def method(cls):
        print(cls.colour)

    @classmethod
    def changeClsColour(cls, colour):
        cls.colour = colour

t = car("red")

t2 = car("blue")

t2.method()
print(t2.colour)

t.method()
print(t.colour)

car.changeClsColour("white")

t2.method()
print(t2.colour)

t.method()
print(t.colour)

t3 = car("pink", "rainbow")

t2.method()
print(t2.colour)

t.method()
print(t.colour)