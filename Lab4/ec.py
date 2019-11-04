import math
import random
from functools import reduce


class EllipticCurve:
    def __init__(self, config):
        self.m = config["m"]
        self.fx = self.parse_value_fx(config["fx"])
        self.a = config["A"]
        self.b = self.parse_value_b(config["B"])
        mmm = (self.convert_int_to_polynomial(self.b))
        nums = []
        counter = 0
        for i in range(len(mmm) - 1, -1, -1):
            if mmm[i] == 1:
                nums.append(counter)
            counter += 1
        nums_r = nums[::-1]
        fff = ""
        for item in nums_r:
            fff += "z^{}+".format(item)
        self.r1 = self.r2 = 1 << self.m
        self.r2 -= 1
        self.poly = reduce(lambda x, y: (x << 1) + y, self.convert_int_to_polynomial(self.fx)[1:])

    @staticmethod
    # додавання ксором
    def my_add(a, b):
        return a ^ b

    @staticmethod
    def bin_to_int(a):
        return int(a, 2)

    @staticmethod
    def parse_value_b(b):
        return int(b, 16)

    def parse_value_fx(self, fx):
        result = ""
        for i in range(self.m, -1, -1):
            if i in fx:
                result += "1"
            else:
                result += "0"
        return self.bin_to_int(result)

    def calc_right_side(self, a, b, x):
        # x * x * x + a * x * x + b
        x2 = self.my_mul(x, x)
        x3 = self.my_mul(x2, x)
        ax2 = self.my_mul(a, x2)
        ax2b = self.my_add(ax2, b)
        x3_ax2b = self.my_add(x3, ax2b)
        return x3_ax2b

    def calc_left_side(self, x, y):
        # y * y + x * y
        return self.my_add(self.my_mul(y, y), self.my_mul(x, y))

    def trace(self, x):
        # Обчислення сліду
        t = x
        for i in range(self.m):
            t = self.my_add(self.my_mul(t, t), x)
        return t % self.fx

    def half_trace(self, x):
        # Обчислення напівсліду
        t = x
        for i in range(int(self.m / 2)):
            t = self.my_add(self.my_mul(self.my_mul(self.my_mul(t, t), t), t), x)
        return t % self.fx

    def generate_point(self, n=1):
        points = []
        deg = self.m
        found = False
        counter = 0
        while counter < n:
            x = random.randint(1, pow(2, deg) - 1 % self.fx)
            y = random.randint(1, pow(2, deg) - 1 % self.fx)
            lef = self.calc_left_side(x, y) % self.fx
            rig = self.calc_right_side(self.a, self.b, x) % self.fx
            if lef == rig:
                points.append(Point(x, y))
                counter += 1
        return points

    def my_mul(self, p1, p2):
        # Множення поліномів
        p = 0
        while p2:
            if p2 & 1:
                p ^= p1
            p1 <<= 1
            if p1 & self.r1:
                p1 ^= self.poly
            p2 >>= 1
        return p & self.r2

    @staticmethod
    def get_degree(a):
        # Визначення степеня полінома
        res = 0
        a >>= 1
        while a != 0:
            a >>= 1
            res += 1
        return res

    @staticmethod
    def convert_int_to_polynomial(num):
        # конвертація цілого числа до вигляду поліному
        return [(num >> i) & 1
                for i in reversed(range(num.bit_length()))]

    def add_points(self, p, q):
        # додавання двох точок
        # if Q = infinity == > P + Q = P
        if q.s == "inf":
            return p
        # if P = infinity == > P + Q = Q
        if p.s == "inf":
            return q
        # P + P
        if p.x == q.x and p.y == q.y and p.s != "inf" and q.s != "inf":
            z3 = self.my_mul(p.x, p.x) % self.fx
            x3 = z3
            x3 = self.my_mul(x3, x3) % self.fx
            x3 = self.my_add(x3, self.b)
            y3 = self.my_mul(z3, self.b)
            az3 = self.my_mul(self.a, z3) % self.fx
            yy = self.my_mul(p.y, p.y) % self.fx
            m = self.my_mod(p=1, k=4) % self.fx
            bm = self.my_mul(self.b, m) % self.fx
            temp = self.my_add(az3, self.my_add(yy, bm)) % self.fx
            temp = self.my_mul(temp, x3) % self.fx
            y3 = self.my_add(temp, y3) % self.fx
        else:
            a = self.my_add(p.y, q.y) % self.fx
            b = self.my_add(p.x, q.x) % self.fx
            temp = self.my_add(self.a, b) % self.fx
            z3 = self.my_mul(b, b) % self.fx
            d = self.my_mul(z3, temp) % self.fx
            e_c = self.my_mul(a, b) % self.fx
            x3 = self.my_mul(a, a) % self.fx
            x3 = self.my_add(x3, self.my_add(d, e_c)) % self.fx
            f = self.my_mul(q.x, z3) % self.fx
            f = self.my_add(f, x3) % self.fx
            g = self.my_add(q.x, q.y)
            g = self.my_mul(g, self.my_mul(z3, z3)) % self.fx
            y3 = self.my_add(e_c, z3)
            y3 = self.my_mul(y3, f)
            y3 = self.my_add(y3, g)
        if z3 == 0:
            return Point(s="inf")
        x3 = self.my_mul(x3, self.inversion(z3)) % self.fx
        z3 = self.my_mul(z3, z3) % self.fx
        y3 = self.my_mul(y3, self.inversion(z3)) % self.fx
        return Point(x3, y3)

    def k_point(self, k, p):
        # множення точки на число
        a = k
        b = Point(s="inf")
        c = p
        while a > 0:
            if a % 2 == 0:
                a //= 2
                c = self.add_points(c, c)
            else:
                a -= 1
                b = self.add_points(b, c)
        return b

    def inversion(self, p):
        if p == 0:
            return None
        return self.my_mod(p, (1 << self.get_degree(self.fx)) - 2)

    def my_mod(self, p, k):
        temp = p
        result = 1
        while k > 0:
            if k % 2 == 1:
                result = self.my_mul(result, temp) % self.fx
            k //= 2
            temp = self.my_mul(temp, temp) % self.fx
        return result

    def logarithm(self, p, q):
        # kQ=P
        temp = 1 << self.get_degree(self.fx)
        n = int(temp + 1 + 2 * math.sqrt(temp))
        b = Point(s="inf")
        for k in range(1, n + 1):
            b = self.add_points(b, q)
            if p.x == b.x and p.y == b.y and p.s != "inf" and b.s != "inf":
                return k
        return -1


class Point:
    def __init__(self, x=0, y=0, s=""):
        self.x = x
        self.y = y
        self.s = s

    def print(self):
        return "infinity" if self.s == "inf" else [self.x, self.y]
