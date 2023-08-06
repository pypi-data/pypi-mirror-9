import builtins
import types

from codeviking.contracts.conditions import SignatureCheck, Precondition, \
    Postcondition, Invariant
from codeviking.contracts.switch import Switch
from .decorator import SwitchedDecorator


def class_check_sig(cls):
    """
    Class decorator that applies `function_check_sig` to all of the callables
    in the body of `cls`.  You can avoid using this decorator directly in
    most circumstances, as it is called by ``check_sig`` if the target is a
    class.

    :param cls: The class to decorate
    :type cls: type
    :return: the decorated class
    :rtype: type
    """
    for (name, member) in cls.__dict__.items():
        tm = type(member)
        # TODO: handle docstrings and function signatures properly.
        if tm is types.FunctionType:
            f = function_check_sig(member)
            f.__name__ = name
            setattr(cls, name, f)
        elif tm is builtins.staticmethod(member):
            # TODO: Handle staticmethods differently
            f = function_check_sig(member)
            f.__name__ = name
            setattr(cls, name, f)
        elif tm is builtins.classmethod(member):
            # TODO: Handle staticmethods differently
            f = function_check_sig(member)
            f.__name__ = name
            setattr(cls, name, f)
    return cls


function_check_sig = SignatureCheck()


def real_check_sig(target):
    """
    Decorator that validates classes or functions that are have annotated
    function arguments.  objects are only decorated if contracts are enabled
    (see functions `enable_contracts` and `disable_contracts`).  If contracts
    are enabled, this function will call function_contract on functions,
    and class_check_sig on classes.

    :param target: the object to be annotated
    :type target: type or callable
    :return: the decorated object
    :rtype: type or callable
    """
    if isinstance(target, type):
        return class_check_sig(target)
    if callable(target):
        return function_check_sig(target)
    raise ValueError(
        "Unable to apply check_sig decorator to %s." % str(target))


contracts = Switch(enabled=True)

check_sig = SwitchedDecorator(real_check_sig, master=contracts)

precondition = SwitchedDecorator(Precondition,
                                 takes_args=True,
                                 master=contracts)

postcondition = SwitchedDecorator(Postcondition,
                                  takes_args=True,
                                  master=contracts)

invariant = SwitchedDecorator(Invariant,
                              takes_args=True,
                              master=contracts)

