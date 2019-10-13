class GeneralWalk:
    def __init__(self, s=None, t=None, g_s=None, g_t=None):
        self.s = s
        self.t = t
        self.g_s = g_s
        self.g_t = g_t

    def next_point(self, prev):
        result = prev

        if self.s is not None and self.g_s is not None:
            result += self.g_s(prev) * self.s

        if self.t is not None and self.g_t is not None:
            result += self.g_t(prev) * self.t

        return result


class PolynomialFunction:
    def __init__(self, polynomial, dim):
        self.polynomial = polynomial
        self.dim = dim

    def eval(self, prev):
        n = int(self.polynomial(prev[:self.dim]))
        return n
