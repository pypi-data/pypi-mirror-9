from forbiddenfruit import curse


def _return_self(self):
    return self


def length(self):
    return len(self)


def to_s(self):
    return str(self)


def to_i(self):
    return int(self)


def to_f(self):
    return float(self)


def _sum(self):  # avoid keyword `sum`
    return sum(self)


def instance_of(self, t):
    return isinstance(self, t)


curse(int, "instance_of", instance_of)
curse(int, "to_s", to_s)
curse(int, "to_f", to_f)

curse(float, "instance_of", instance_of)
curse(float, "to_s", to_s)
curse(float, "to_i", to_i)

curse(str, "instance_of", instance_of)
curse(str, "length", property(length))
curse(str, "to_i", to_i)
curse(str, "to_f", to_f)
curse(str, "to_s", _return_self)

curse(unicode, "instance_of", instance_of)
curse(unicode, "length", property(length))
curse(unicode, "to_i", to_i)
curse(unicode, "to_f", to_f)
curse(unicode, "to_s", _return_self)

curse(list, "instance_of", instance_of)
curse(list, "length", property(length))
curse(list, "sum", _sum)

curse(tuple, "instance_of", instance_of)
curse(tuple, "length", property(length))
curse(tuple, "sum", _sum)
