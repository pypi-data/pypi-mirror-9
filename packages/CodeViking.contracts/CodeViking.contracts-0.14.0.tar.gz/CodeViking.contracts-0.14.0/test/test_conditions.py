import math

import pytest

from codeviking.contracts.argcheckers import Gt
from codeviking.contracts.contracts import precondition, postcondition, \
    invariant
from codeviking.contracts.error import PreconditionViolation, \
    TypeCheckViolation, \
    FunctionCheckViolation, InvariantViolation, InvariantError
from codeviking.contracts.types import NamedTuple


GLOBAL_X = None


def global_x_is_none(*_):
    a = GLOBAL_X
    r = (a is None)
    return r


@precondition(global_x_is_none)
def f(x):
    return x + 1


TOLERANCE = 1E-7


def float_near(value, other, tol=TOLERANCE):
    if abs(other) < tol and abs(value) < tol:
        return True
    re = abs(other) - abs(value)
    re /= min(abs(other), abs(value))
    return re < tol


class A:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    @invariant(lambda s: s.x)
    @invariant(lambda s: s.y)
    def is_zero(self):
        return self.x == 0.0 and self.y == 0.0

    @precondition(lambda s: not s.is_zero)
    def invsq_dist(self):
        return 1.0 / (self.x * self.x + self.y * self.y)

    @invariant(lambda s, _: s.a)
    def set_a(self, new_a):
        # noinspection PyAttributeOutsideInit
        self.a = new_a

    @invariant(lambda s, _: s.x)
    def set_x(self, new_x):
        self.x = new_x

    @property
    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    @precondition(lambda s: not s.is_zero)
    @postcondition(lambda s: float_near(s.length, 1.0))
    def unitize(self):
        r = self.length
        self.x /= r
        self.y /= r


def test_g_precondition_fail():
    global GLOBAL_X
    GLOBAL_X = 4
    with pytest.raises(PreconditionViolation):
        print(f(2))


def test_g_precondition():
    global GLOBAL_X
    GLOBAL_X = None
    GLOBAL_X = f(2)


def test_class_precondition_fail():
    p = A(0.0, 0.0)
    with pytest.raises(PreconditionViolation):
        _ = p.invsq_dist()


def test_class_precondition():
    p = A(1.0, 0.0)
    _ = p.invsq_dist()


def test_pre_postcondition():
    p = A(2.0, -2.0)
    p.unitize()


def test_pre_postcondition_fail():
    p = A(0.0, 0.0)
    with pytest.raises(PreconditionViolation):
        p.unitize()


NT = NamedTuple('NT', [('a', int), ('b', Gt(0))])


def test_nt_checker():
    n = NT(5, 3)
    assert n.a == 5
    assert n.b == 3


def test_nt_checker_fail_1():
    with pytest.raises(TypeCheckViolation):
        _ = NT(5.0, 3)


def test_nt_checker_fail_2():
    with pytest.raises(FunctionCheckViolation):
        _ = NT(5, -3)


def test_nt_checker_fail_3():
    with pytest.raises(TypeCheckViolation):
        _ = NT(5.0, -3)


def test_invariant_error():
    p = A(1.0, 1.0)
    with pytest.raises(InvariantError):
        p.set_a(7.0)


def test_invariant_violation():
    p = A(1.0, 1.0)
    with pytest.raises(InvariantViolation):
        p.set_x(7.0)



