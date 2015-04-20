class my_str:
    def __init__(self):
        self.s = ""
    def __add__(self, other):
        self.s += str(other)
        return self
    def __str__(self):
        return self.s

s = my_str()
s = s + 5
print(s+4)
