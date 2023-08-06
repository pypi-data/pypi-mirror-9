from codeviking.contracts.argcheckers import ContractWrapper


class Contract:
    pass


class LazyEvaluator:
    """
    Store an expression and a context, and evaluate that expression at a
    later time
    """

    def __init__(self, expression, global_vars, local_vars):
        """
        :param expression: The expression to evaluate.
        :type expression: str
        :param global_vars: the global variables
        :param local_vars:
        """
        self._expression = expression
        self._context = (global_vars, local_vars)
        self._globals = global_vars
        self._locals = local_vars

    def evaluate(self):
        eval(self._expression, self._globals, self._locals)


class Precondition(Contract):
    def __init__(self, precondition_func):
        self._precondition_func = precondition_func

    def __call__(self, target):
        result = None
        if not isinstance(target, ContractWrapper):
            assert callable(target)
            # We're wrapping a regular function.  We need to create a new
            # ContractWrapper that contains it.
            target = ContractWrapper(target)
        # we're wrapping around an existing ContractWrapper, so we just add
        # this Precondition to the existing wrapper and return it.
        target._add_precondition(self._precondition_func)
        return target


class Postcondition(Contract):
    def __init__(self, postcondition_func):
        self._postcondition_func = postcondition_func

    def __call__(self, target):
        result = None
        if not isinstance(target, ContractWrapper):
            assert callable(target)
            # We're wrapping a regular function.  We need to create a new afd
            # ContractWrapper that contains it.
            target = ContractWrapper(target)
        # we're wrapping around an existing ContractWrapper, so we just
        # this Postcondition to the existing wrapper and return it.
        target._add_postcondition(self._postcondition_func)
        return target


class Invariant(Contract):
    def __init__(self, invariant_func):
        self._invariant_func = invariant_func

    def __call__(self, target):
        result = None
        if not isinstance(target, ContractWrapper):
            assert callable(target)
            # We're wrapping a regular function.  We need to create a new add
            # ContractWrapper that contains it.
            target = ContractWrapper(target)
        # we're wrapping around an existing ContractWrapper, so we just
        # this Invariant to the existing wrapper and return it.
        target._add_invariant(self._invariant_func)
        return target


class SignatureCheck(Contract):
    def __call__(self, target):
        result = None
        if not isinstance(target, ContractWrapper):
            assert callable(target)
            # We're wrapping a regular function.  We need to create a new
            # ContractWrapper that contains it.
            target = ContractWrapper(target)
        # we're wrapping around an existing ContractWrapper, so we just
        # this SignatureCheck to the existing wrapper and return it.
        target._add_signature_check()
        return target


"""
An invariant is different from preconditions and postconditions.  Invariants
are not responsible for determining if they fail or succeed.  An invariant is
just a function evaluation.  Only the contract wrapper can tell if the pre-
and post- evaluations of an invariant match.

An invariant can, however, forward on exception from one of the checkers that
it calls.

"""""

"""

Preconditions and Postconditions
--------------------------------

A condition should return True if it has succeeded.  If it has failed,
it should raise either a PreconditionViolation or PostconditionViolation
exception.
But, there are other places that an exception can occur when checking a
condition.  If the violation occurs in user code, or in a contract that checks a
function that is called during the condition evaluation, we need to forward
that error to the user.  Note that this sort of violation does not cause THIS
condition to fail - the violation occurred before we could finish determining
whether this condition failed.

This may sound like a subtle difference, but it is very important.  We want
the user to be able to find out exactly where the error occurs.  A contract
violation occurs at the deepest level of nesting that caused the violation.

Exceptions that we want to pass on to the user:

  * Violations that occur when calling a wrapped function.  These aren't due to
    any contract violations.
  * Violations that occur in a failed contract that was called from this one.
  * Violations in any of the user-defined functions that are called from within
    the body of a contract.  It is especially important to forward these.  If
    we don't, then the user will only receive contract-related exceptions,
    even if their code is the problem.


Custom Conditions and Checkers.
-------------------------------

A custom condition just needs to return True if it has succeeded.  If it
fails, it should return False, OR raise an appropriate exception.  Returning
False should *only* be done when the violation occurred in the current
conditon.  If the violation occurred in a nested contract:

  * if the subcontract returns False, an exception should be raised.
  * if the subcontract raises an exception, that exception should be
    allowed to bubble up past your contract.

Generally, you don't have to worry about catching any exceptions.  You can
just let them bubble up to the wrapper function.  It will which exceptions to
catch.


"""
