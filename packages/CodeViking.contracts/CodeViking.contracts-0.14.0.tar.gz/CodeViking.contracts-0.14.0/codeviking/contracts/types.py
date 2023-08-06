from collections import namedtuple

from codeviking.contracts.argcheckers import TupleArgChecker


__author__ = 'dan'


def NamedTuple(name, elements):
    """
    Create a new named tuple class.
    :param name: the name of the class
    :type name: str
    :param elements: ordered list of fields: (field_name, field_checker)
    :type elements: list[(str, ArgCheck)]
    :return: the class
    :rtype: namedtuple
    """
    # TODO fix this so keyword parameters can be used in the constructor
    elem_names = [n for (n, c) in elements]
    checkers = [c for (n, c) in elements]
    checker = TupleArgChecker(checkers)
    T = namedtuple(name, elem_names)
    orig_new = T.__new__

    def __new__(*args):
        ok = checker(args[1:], T.__new__.__globals__)
        return orig_new(*args)

    T.__new__ = __new__
    T.__name__ = name
    return T
