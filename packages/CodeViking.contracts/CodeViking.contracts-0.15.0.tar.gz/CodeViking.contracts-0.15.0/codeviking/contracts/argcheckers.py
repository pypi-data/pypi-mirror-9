import inspect
from collections import abc
from .error import CheckError

from codeviking.contracts.error import PreconditionError, \
    PreconditionViolation, InvariantError, SignatureError, SignatureViolation, \
    ReturnSignatureViolation, InvariantViolation, PostconditionError, \
    PostconditionViolation
from .error import AnnotationError, CheckViolation, \
    ElementCheckViolation, ContractError, \
    UnionCheckViolation, LengthMismatchViolation, \
    TypeCheckViolation, FunctionCheckViolation


class Checker:
    def __init__(self, to_str_func):
        self._to_str_func = to_str_func
    def __str__(self):
        return self._to_str_func(self)
    def __call__(self, arg, eval_scope):
        pass

class UnscopedChecker(Checker):
    """
    Checker that uses a function to validate an argument.  The function takes
    only the argument, not an evaluation scope.
    """

    def __init__(self, func, to_str_func=None):
        """
        Uses the function `func` to validate an argument.

        When an arg or return value needs to be validated, func(arg) is
        called.  If the function returns True, the condition is satisfied.

        :param func: argument checking function that must be satisfied.
        :type func:  f(arg) -> bool
        :param to_str_func: function that returns a string representation of
            this object, or None if func.__name__ should be used.
        :type to_str_func: None | (UnscopedChecker) -> str
        """
        if to_str_func is None:
            if hasattr(func, '__name__'):
                to_str_func = lambda s: s._func.__name__
            else:
                to_str_func = lambda s: str(s._func)
        super().__init__(to_str_func)
        self._func = func
        if not callable(self._func):
            raise ValueError("Cannot create an UnscopedChecker from func={func}.  "
                             "func must be a function that takes one "
                             "argument.".format(func=func))

    def __call__(self, arg, eval_scope):
        try:
            result = self._func(arg)
        except Exception as e:
            if not isinstance(e, TypeCheckViolation):
                raise CheckError(message="An exception was raised while "
                                           "evaluating UnscopedChecker function: "
                                           "{func}\n"
                                           "on argument: {arg}\n"
                                           "If this is a Checker in the "
                                           "contracts package, please file a "
                                           "bug "
                                           "report.\n".format(
                    func=self._func.__name__,
                    arg=str(arg)),
                                   arg=arg) from e
            else:
                raise
        if result:
            return result
        # The function returned False.  We'll raise a CheckViolation for it.
        raise FunctionCheckViolation(function=self._func, value=arg)


class ScopedChecker(Checker):
    """
    Checker that uses a function to validate an argument.  The function takes
    the argument to validate and a scope in which to evaluate it.
    """

    def __init__(self, func, to_str_func=None):
        """
        Uses the function `func` to validate an argument.

        When an arg or return value needs to be validated,
        func(arg, eval_scope) is called.  If the function returns True,
        the condition is satisfied.

        :param func: argument checking function that must be satisfied.
        :type func:  f(arg, eval_scope) -> bool
        :param to_str_func: function that returns a string representation of
            this object, or None if func.__name__ should be used.
        :type to_str_func: None | (UnscopedChecker) -> str
        """
        if to_str_func is None:
            if hasattr(func, '__name__'):
                to_str_func = lambda s: s._func.__name__
            else:
                to_str_func = lambda s: str(s._func)
        super().__init__(to_str_func)
        self._func = func
        if not callable(self._func):
            raise ValueError("Cannot create an ScopedChecker from func={func}.  "
                             "func must be a function that takes two "
                             "arguments.".format(func=func))

    def __call__(self, arg, eval_scope):
        try:
            result = self._func(arg, eval_scope)
        except Exception as e:
            if not isinstance(e, CheckViolation):
                raise CheckError(message="An exception was raised while "
                                           "evaluating ScopedChecker function: "
                                           "{func}\n"
                                           "on argument: {arg}\n"
                                           "If this is a Checker in the "
                                           "contracts package, please file a "
                                           "bug "
                                           "report.\n".format(
                    func=self._func.__name__,
                    arg=str(arg)),
                                   arg=arg) from e
            else:
                raise
        if result:
            return result
        # The function returned False.  We'll raise a CheckViolation for it.
        raise FunctionCheckViolation(function=self._func, value=arg)


Any = UnscopedChecker(lambda x: True, lambda slf: 'Any')


class Is(UnscopedChecker):
    """
    ArgChecker that is satisfied when an arg is the same object as another.
    """

    def __init__(self, compare_to):
        """
        :param compare_to: the object to compare the argument to
        :type compare_to: any
        """
        self._compare_to = compare_to
        super().__init__(lambda x: x is compare_to)

    def __str__(self):
        if self._compare_to is None:
            return str(None)
        if type(self._compare_to) in (int, float, str):
            return str(self._compare_to)
        return "Is(%s)" % str(self._compare_to)


class Option(ScopedChecker):
    """
    An ArgChecker that is satisfied when the argument satisfies its
    inner_checker, or when the argument is None
    """

    def __init__(self, inner_checker):
        inner_checker = make_arg_checker(inner_checker)
        self._inner_checker = inner_checker
        super().__init__(lambda x, eval_scope: x is None or
                                               inner_checker(x, eval_scope))

    def __str__(self):
        return "Option(%s)" % str(self._inner_checker)


# Start Comparison Checkers

class Cmp(UnscopedChecker):
    def __init__(self, value, cmp_func, format_string):
        super().__init__(lambda x: cmp_func(x, value))
        self._value = value
        self._cmp_func = cmp_func
        self._format = format_string

    def __str__(self):
        return self._format % self._value


class Eq(Cmp):
    def __init__(self, value):
        super().__init__(value, lambda a, b: a == b, "value == %s")


class Neq(Cmp):
    def __init__(self, value):
        super().__init__(value, lambda a, b: a != b, "value != %s")


class Lt(Cmp):
    def __init__(self, value):
        super().__init__(value, lambda a, b: a < b, "value < %s")


class Gt(Cmp):
    def __init__(self, value):
        super().__init__(value, lambda a, b: a > b, "value > %s")


class Leq(Cmp):
    def __init__(self, value):
        super().__init__(value, lambda a, b: a <= b, "value <= %s")


class Geq(Cmp):
    def __init__(self, value):
        super().__init__(value, lambda a, b: a >= b, "value >= %s")


# End Comparison Checkers




class Iterable(ScopedChecker):
    def __init__(self, element_checker, expected_type=abc.Iterable):
        """
        A Checker that is satisfied if the arg is iterable, and all the
        elements of the list satisfy `element_checker`
        """
        self._element_checker = make_arg_checker(element_checker)

        def f(x, eval_scope):
            if not isinstance(x, expected_type):
                raise TypeCheckViolation(value=x,
                                         expected_type=expected_type)
            for e in x:
                if not self._element_checker(e, eval_scope):
                    raise ElementCheckViolation(self._element_checker, e)
            return True

        super().__init__(f)

    def __str__(self):
        return "%s(%s)" % (str(self.__class__.__name__),
                           str(self._element_checker))


class Seq(Iterable):
    def __init__(self, element_checker):
        super().__init__(element_checker, abc.Sequence)


class Set(Iterable):
    def __init__(self, element_checker):
        super().__init__(element_checker, abc.Set)

    def __str__(self):
        return "Set(%s)" % (str(self._element_checker))


class Dict(ScopedChecker):
    def __init__(self, key_checker, value_checker):
        """
        An ArgChecker that is satisfied if the arg is an instance of dict,
        if the keys all satisfy `key_checker`, and the values all satisfy
        `value_checker`
        """
        self._key_checker = make_arg_checker(key_checker)
        self._value_checker = make_arg_checker(value_checker)

        def f(d, eval_scope):
            if not isinstance(d, dict):
                raise TypeCheckViolation(value=d, expected_type=dict)
            for (k, v) in d.items():
                if not self._key_checker(k, eval_scope):
                    return False
                if not self._value_checker(v, eval_scope):
                    return False
            return True

        super().__init__(f)

    def __str__(self):
        return "{%s: %s}" % (str(self._key_checker),
                             str(self._value_checker))


class Union(ScopedChecker):
    def __init__(self, *arg_checkers):
        """
        An ArgChecker that is satisfied if one or more of the ArgCheckers in
        `arg_checkers` are satisfied.
        """
        self._all_checkers = [make_arg_checker(c) for c in arg_checkers]

        def f(x, eval_scope):
            if len(self._all_checkers) == 0:
                return True
            violations = list()
            for c in self._all_checkers:
                try:
                    if c(x, eval_scope):
                        return True
                    else:
                        violations.append((c, False))
                except Exception as e:
                    violations.append((c, e))
            message = []
            for (c, v) in violations:
                if not v:
                    message.append("Checker '{checker}' returned "
                                   "False for value {value}".format(
                        checker=str(c),
                        value=str(v)))
                else:
                    message.extend(v.message.splitlines())
            message = ["  " + line for line in message]
            raise UnionCheckViolation(message_lines=message,
                                      value=x)


        super().__init__(f)

    def __str__(self):
        checkers = [str(c) for c in self._all_checkers]
        checkers.sort()
        return "{%s}" % (", ".join(checkers))


# Begin internal ArgCheckers - these contracts usually shouldn't be
# instantiated in user code.  They are automatically created in
# `make_arg_checker` from the appropriate annotations.


class AllOf(ScopedChecker):
    def __init__(self, *arg_checkers):
        """
        An ArgChecker that is satisfied if all of the ArgCheckers in
        `arg_checkers` are satisfied.
        """
        self._all_checkers = [make_arg_checker(c) for c in arg_checkers]

        def f(x, eval_scope):
            for c in self._all_checkers:
                if not c(x, eval_scope):
                    return False
            return True

        super().__init__(f)

    def __str__(self):
        return "AllOf(%s)" % (", ".join([str(c) for c in self._all_checkers]))


class TypeArgChecker(ScopedChecker):
    def __init__(self, ctype):
        """
        An ArgChecker that is satisfied if the argument is an instance of
        type `ctype`
        """
        self._ctype = ctype

        def check_type(value, eval_scope):
            if isinstance(value, ctype):
                return True
            raise TypeCheckViolation(value=value, expected_type=ctype)

        super().__init__(check_type)

    def __str__(self):
        return self._ctype.__name__


class TupleArgChecker(ScopedChecker):
    def __init__(self, checkers):
        """
        An ArgChecker that is satisfied if the argument is an ordered sequence
        whose ith element satisfies the ith checker.
        """
        arg_checkers = tuple(make_arg_checker(a) for a in checkers)
        self._arg_checkers = arg_checkers
        def f(arg, eval_scope):
            expected_length = len(self._arg_checkers)

            try:
                arg_len = len(arg)
            except TypeError as e:
                raise TypeCheckViolation(value=arg, expected_type=Seq)
            if expected_length != arg_len:
                raise LengthMismatchViolation(value=arg,
                                              expected_length=expected_length)
            try:
                for i in range(len(self._arg_checkers)):
                    r = self._arg_checkers[i](arg[i], eval_scope)
                    if not r:
                        return False
            except CheckViolation as e:
                raise
            return True
        def to_str(s):
            return "(%s)" % (", ".join([str(c) for c in s._arg_checkers]))
        super().__init__(f, to_str)


class DelayedEvalChecker(ScopedChecker):
    """
    A Checker that is not built until the first time it checks an argument.
    """
    def __init__(self, expression):
        if not isinstance(expression, str):
            raise ValueError("expression must be a string.")
        self._expression = expression
        self._checker = None
        def f(arg, eval_scope):
            if self._checker is None:
                # checker has not been evaluated yet, so we do that now.
                try:
                    self._checker = make_arg_checker(eval(self._expression,
                                                          eval_scope))
                except Exception as e:
                    raise CheckError("DelayedEvalChecker is unable to evaluate "
                                     "expression %s " % str(
                        self._expression)) from e
            return self._checker(arg, eval_scope)

        super().__init__(f, lambda s: s._expression)



# End internal arg checkers


def make_arg_checker(annotation):
    """
    Make a ArgChecker from an argument annotation.

    This function is mostly for internal use.  It is called by
    ``function_check_sig``

    :param annotation: the argument annotation
    :type annotation: ArgChecker, None, type, callable, str, set, tuple, list
    :param eval_scope: the scope in which to evaluate the annotation.  This is
        only relevant for checkers that must be lazily evaluated (like
        "ClassName").  Usually, this will be the scope in which the function
        is defined.
    :return: an ArgChecker
    :rtype: function that takes any argument and returns a boolean if the
            argument satisfies the checker.

    """
    if isinstance(annotation, Checker):
        return annotation
    if annotation is None:
        return Is(None)
    if isinstance(annotation, type):
        return TypeArgChecker(annotation)
    if isinstance(annotation, dict):
        items = list(annotation.items())
        if len(items) != 1:
            raise AnnotationError("dict annotation must have only one (key, "
                                  "value) pair")
        key_check, value_check = items[0]
        return Dict(key_check, value_check)
    if isinstance(annotation, tuple):
        return TupleArgChecker(annotation)
    if isinstance(annotation, list):
        return AllOf(*annotation)
    if isinstance(annotation, str):
        return DelayedEvalChecker(annotation)
    if isinstance(annotation, set):
        return Union(*annotation)
    if callable(annotation):
        return UnscopedChecker(annotation)
    raise ContractError("Invalid contract '%s'" % str(annotation))


class ContractWrapper:
    """
    This serves as a unified wrapper that can contain multiple Contracts
    operating on the same target function.

    :param target: the target function that will be wrapped.
    """

    def __init__(self, target):
        self._target = target
        self._preconditions = list()
        self._postconditions = list()
        self._invariants = list()
        self._arg_checkers = None
        self._return_check = None

    def __get__(self, obj, _):
        # this is required in order to support instance methods
        from functools import partial

        return partial(self.__call__, obj)

    def _add_invariant(self, invariant):
        self._invariants.insert(0, invariant)

    def _add_precondition(self, precondition):
        self._preconditions.insert(0, precondition)

    def _add_postcondition(self, postcondition):
        self._postconditions.insert(0, postcondition)

    def _add_signature_check(self):
        if self._arg_checkers is not None or self._return_check is not None:
            raise ContractError("A function signature check has already been "
                                "added to the target function:  {"
                                "target}".format(target=self._target))

        self._arg_checkers = dict()
        self._signature = inspect.signature(self._target)

        # build a checker for the return annotation, if it is non-empty
        if self._signature.return_annotation is not inspect.Signature.empty:
            self._return_check = make_arg_checker(
                self._signature.return_annotation)

        self._eval_scope = self._target.__globals__
        # build a checker for each non-empty parameter annotation
        for name, p in self._signature.parameters.items() :
            if p.annotation is not inspect.Signature.empty:
                self._arg_checkers[name] = make_arg_checker(p.annotation)
        if len(self._arg_checkers) == 0:
            self._arg_checkers = None


    def __call__(self, *args, **kwargs):

        for prc in self._preconditions:
            try:
                r = prc(*args, **kwargs)
            except Exception as e:
                raise PreconditionError(target=self._target,
                                        condition=prc,
                                        args=args,
                                        kwargs=kwargs) from e
            if not r:
                raise PreconditionViolation(target=self._target,
                                            condition=prc,
                                            args=args,
                                            kwargs=kwargs)

        # get all the invariants and store their values
        pre_invariants = []
        for invc in self._invariants:
            try:
                v = invc(*args, **kwargs)
            except Exception as e:
                raise InvariantError(target=self._target,
                                     invariant=invc,
                                     when="before",
                                     args=args,
                                     kwargs=kwargs) from e
            pre_invariants.append(v)

        # now we can check the arguments
        if self._arg_checkers is not None:
            call_args = inspect.getcallargs(self._target, *args, **kwargs)
            for (arg_name, arg_value) in call_args.items():
                if arg_name not in self._arg_checkers:
                    continue
                checker = self._arg_checkers[arg_name]
                try:
                    success = checker(arg_value, self._eval_scope)
                except TypeCheckViolation:
                    raise
                except Exception as e:
                    raise SignatureError(target=self._target,
                                         arg_name=arg_name,
                                         arg_checker=checker,
                                         arg_value=arg_value) from e
                if not success:
                    raise SignatureViolation(target=self._target,
                                             arg_name=arg_name,
                                             arg_checker=checker,
                                             arg_value=arg_value)  # TODO
        # now we actually call the function
        # we need to carefully catch any exceptions that are emitted by the
        # check_sig system.  These should just be forwarded to the caller (
        # otherwise, it will cause the check_sig on this function to fail).
        return_value = self._target(*args, **kwargs)


        # now we can check the return value
        if self._return_check is not None:
            try:
                # noinspection PyCallingNonCallable
                return_success = self._return_check(return_value,
                                                    self._eval_scope)
                # TODO
            except Exception as e:
                raise SignatureError(target=self._target,
                                     arg_name='return',
                                     arg_checker=self._return_check,
                                     arg_value=return_value) from e
            if not return_success:
                raise ReturnSignatureViolation(target=self._target,
                                               return_checker=self._return_check,
                                               return_value=return_value)

        # Calculate all of the post-function call invariant values
        post_invariants = []
        for invc in self._invariants:
            try:
                v = invc(*args, **kwargs)
            except Exception as e:
                raise InvariantError(target=self._target,
                                     invariant=invc,
                                     when="after",
                                     args=args,
                                     kwargs=kwargs) from e
            post_invariants.append(v)

        # Compare pre-function call and post-function call invariant values.
        # If they don't agree, we raise an InvariantViolation
        for i in range(len(self._invariants)):
            if pre_invariants[i] != post_invariants[i]:
                failed = self._invariants[i]
                raise InvariantViolation(target=self._target,
                                         args=args,
                                         kwargs=kwargs,
                                         invariant=failed,
                                         pre_val=pre_invariants[i],
                                         post_val=post_invariants[i],
                                         return_value=return_value
                )  # TODO
        for postc in self._postconditions:
            try:
                r = postc(*args, **kwargs)
            except Exception as e:
                raise PostconditionError(target=self._target,
                                         condition=postc,
                                         args=args,
                                         kwargs=kwargs) from e
            if not r:
                raise PostconditionViolation(target=self._target,
                                             condition=postc,
                                             args=args,
                                             kwargs=kwargs)

        return return_value
