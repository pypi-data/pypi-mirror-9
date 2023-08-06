import functools

import pytest

from codeviking.contracts.decorator import Switch, SwitchedDecorator


__author__ = 'dan'


@pytest.fixture
def decorators():
    master = Switch()

    def wrap1(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = {'result': func(*args, **kwargs)}
            return result

        return wrapper

    def wrap2(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = {'result': func(*args, **kwargs)}
            return result

        return wrapper

    decorators = (SwitchedDecorator(wrap1),
                  SwitchedDecorator(wrap2,
                                    master=master))
    return decorators, master


def dec_f1_f2(decs):
    print(decs)
    d1, d2 = decs

    @d1
    def f1(x):
        return x + 1

    @d2
    def f2(x):
        return x - 1

    return f1, f2


@pytest.fixture(params=[(False, False),
                        (False, True),
                        (True, False),
                        (True, True), ])
def enable_combos(request):
    return request.param


def test_call(decorators, enable_combos):
    enable_master, enable_indep = enable_combos
    decs, master = decorators
    indep, dep = decs
    master = decorators[1]
    master.enabled = enable_master
    indep.enabled = enable_indep

    f1, f2 = dec_f1_f2((indep, dep))

    assert (master.enabled == enable_master)
    assert (indep.enabled == enable_indep)

    assert (callable(f1))
    assert (callable(f2))

    xx = 10
    result_indep = xx + 1
    result_dep = xx - 1

    if enable_master:
        result_dep = {'result': result_dep}
    if enable_indep:
        result_indep = {'result': result_indep}

    assert (f1(xx) == result_indep)
    assert (f2(xx) == result_dep)
