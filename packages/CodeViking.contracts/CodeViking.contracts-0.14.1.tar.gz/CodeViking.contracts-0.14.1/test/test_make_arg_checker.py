import pytest

from codeviking.contracts.argcheckers import make_arg_checker
from .annotation_data import ARG_AS_STR, ARG_VIOLATION, ARG_SUCCESS


@pytest.fixture(params=ARG_AS_STR)
def arg_str(request):
    arg, expected_str = request.param
    return arg, expected_str


@pytest.fixture(params=ARG_SUCCESS)
def arg_success(request):
    return request.param


@pytest.fixture(params=ARG_VIOLATION)
def arg_violation(request):
    return request.param


def test_arg_str(arg_str):
    arg, expected_str = arg_str
    a = make_arg_checker(arg)
    a_str = str(a)
    assert (a_str == expected_str)


def test_arg_success(arg_success):
    arg, success = arg_success
    a = make_arg_checker(arg)
    assert a(success, globals())


def test_arg_violation(arg_violation):
    arg, violation, exception = arg_violation
    assert exception is not None
    a = make_arg_checker(arg)
    try:
        _ = a(violation, globals())
    except Exception as e:
        if isinstance(e, exception):
            assert True
    else:
        raise Exception("Exception %s was expected.\narg=%s\nviolation=%s\n" % (
            str(exception.__name__),
            str(a),
            str(violation)))

