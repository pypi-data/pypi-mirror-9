import functools

import pytest

from codeviking.contracts.decorator import DecoratorGroup


__author__ = 'dan'


@pytest.fixture
def wrappers():
    def wrap1(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = {'result1': func(*args, **kwargs)}
            return result

        return wrapper

    def wrap2(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = {'result2': func(*args, **kwargs)}
            return result

        return wrapper

    return wrap1, wrap2


@pytest.fixture(params=[True, False])
def enabled(request):
    return request.param


def test_call(wrappers, enabled):
    w1, w2 = wrappers
    g = DecoratorGroup({'d1': w1,
                        'd2': w2})
    g.enabled = enabled

    @g.d1
    def f1(x):
        return x + 1

    @g.d2
    def f2(x):
        return x - 1

    assert (g.enabled == enabled)
    assert (g.d1.enabled == enabled)
    assert (g.d2.enabled == enabled)

    assert (callable(f1))
    assert (callable(f2))

    xx = 10
    result_f1 = xx + 1
    result_f2 = xx - 1

    if enabled:
        result_f1 = {'result1': result_f1}
    if enabled:
        result_f2 = {'result2': result_f2}

    assert (f1(xx) == result_f1)
    assert (f2(xx) == result_f2)

    def ff():
        @g.nonexistent
        def f():
            return 1

        return f()

    pytest.raises(AttributeError, ff)
