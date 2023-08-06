import random

import pytest

from codeviking.contracts import Union, Option, Any, Dict, Seq, contracts, \
    check_sig



# check_sig.enabled = True
from codeviking.contracts.error import TypeCheckViolation

contracts.enabled = True

MAX_DEPTH = 4
DEPTH = 0


def random_any():
    if DEPTH >= MAX_DEPTH:
        return random_choice(
            [random_str, random_int, random_float, lambda: None])
    if DEPTH >= MAX_DEPTH:
        return random_choice(
            [random_str, random_int, random_float, random_tuple,
             random_set, lambda: None])


def random_str():
    n = random.randint(5, 11)
    src = 'abcdefghijklmnopqrstuvwxyz'
    return ''.join([random.choice(src) for _ in range(n)])


def random_int():
    return random.randint(-99, 99)


def random_float():
    return 99.99999 * (random.random() - 0.5)


def random_tuple(f=random_any):
    global DEPTH
    DEPTH += 1
    r = tuple([f() for _ in range(random.randint(2, 6))])
    DEPTH -= 1
    return r


def random_set(f=random_any):
    global DEPTH
    DEPTH += 1
    rr = frozenset([f() for _ in range(random.randint(2, 6))])
    DEPTH -= 1
    return rr


def random_choice(generators):
    return random.choice(generators)()


def test_functions():
    @check_sig
    def f1(x: int, y: Union(float, int), *_a,
         _kw: Option((str, int))=('wine', 78)) -> str:
        return str(x + y)

    @check_sig
    def f2(x: 'int') -> str:
        return str(x)

    def is_smelly_or_negative_int(x):
        if str(x).startswith('smelly'):
            return True
        if isinstance(x, int) and x < 0:
            return True
        return False

    @check_sig
    def f3(x: Seq(({int, str}, int))) -> Dict((int, Any),
                                              Seq(Option(
                                                  is_smelly_or_negative_int))):
        def rand_osi():
            f = [lambda: 'smelly-' + random_str(),
                 lambda: random.randint(-100, -1),
                 lambda: None]
            return random.choice(f)()

        res = dict()
        for (_, __) in x:
            res[(random_int(), random_any())] = [rand_osi() for _ in range(
                random.randint(0, 10))]
        return res

    n = random.randint(10, 20)
    for i in range(n):
        _ = f3(list((random_choice([random_int, random_str]), random_int()) for
                    _ in
                    range(random.randint(10, 20))))


# make several example function signatures that use default arguments,
# arbitrary number of arguments, and keyword arguments.
# figure out how internals are arranged.


@check_sig
class A():
    def __init__(self, a: str, b: int):
        self.a, self.b = a, b

    def fmt(self, pfx: str) -> str:
        return pfx + (str(self.a) + ',' + str(self.b))

    def is_same(self, other: "A") -> bool:
        return self.a == other.a and self.b == other.b

# disable contracts for class B
contracts.enabled = False


@check_sig
class B:
    def __init__(self, a:str, b:str):
        self.a, self.b = a, b

# re-enable contracts
contracts.enabled = True


@check_sig
class C:
    def __init__(self, a:str, b:str):
        self.a, self.b = a, b


def testa():
    aa = A('f', 7)
    print(aa.fmt('::'))


def test_B():
    _ = B(8, 9)


def test_C():
    with pytest.raises(TypeCheckViolation):
        _ = C(8, 9)


def test_A_delayed():
    a1 = A('f', 7)
    a2 = A('f', 7)
    assert a1.is_same(a2)
