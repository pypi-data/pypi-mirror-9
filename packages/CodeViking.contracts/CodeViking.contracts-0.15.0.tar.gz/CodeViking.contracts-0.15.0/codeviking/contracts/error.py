# Error classes


class AnnotationError(Exception):
    """
    An annotation was incorrectly specified.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class ContractError(Exception):
    """
    A check_sig had a fatal error while attempting to validate a check_sig.
    """

    def __init__(self, *, message, target):
        if message is None:
            message = ("Internal Contract Error.  This usually "
                       "indicates a bug inside the contracts "
                       "package.  Please file a bug report.")
        self.message = message
        self.target = target
        super().__init__(message)

    def __str__(self):
        return self.message


class ContractViolation(Exception):
    """
    A check_sig has been violated.  No internal errors have happened, but the
    conditions for satisfying the check_sig have not been met.
    """

    def __init__(self, *, message=None, target):
        if message is None:
            message = "Contract Failed"
        super().__init__(message)
        self.message = message
        self.target = target

    def __str__(self):
        return self.message


class CheckError(Exception):
    def __init__(self, *,
                 message,
                 arg):
        self.message = message
        self.arg = arg
        super().__init__(message)

    def __str__(self):
        return self.message


# start of checkers
# Checkers are used to verify arguments and return arguments.
# These errors should never be caught by the user.  They are intended to be
# caught by the check_sig wrapper.

class CheckViolation(Exception):
    def __init__(self, message, value=None):
        self.value = value
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class FunctionCheckViolation(CheckViolation):
    def __init__(self, *, function, message=None, value=None):
        super().__init__("Check '%s' failed for value '%s'" % (
            str(function.__name__), str(value)),
                         str(value))


class TypeCheckViolation(CheckViolation):
    def __init__(self, *, value, expected_type, message=None):
        if message is None:
            message = ("Expected type: '{expected_type}', actual_type: '{"
                       "actual_type}'\n"
                       "value: '{value}'").format(
                expected_type=expected_type.__name__,
                actual_type=type(value), value=value)
        self.expected_type = expected_type
        super().__init__(message=message, value=value)


class LengthMismatchViolation(CheckViolation):
    def __init__(self, *, message=None, value, expected_length):
        if message is None:
            message = ("Expected item with length={expected_length}, "
                       "but '{value}' has length={actual_length}").format(
                value=value, expected_length=expected_length, actual_length=
                len(value)
            )
        self.expected_length = expected_length
        super().__init__(message, value)


class ContainerCheckViolation(CheckViolation):
    def __init__(self,
                 *
                 value,
                 container_type,
                 element_checker):
        self.element_checker = element_checker
        message = ("Container check violation.  Expected type "
                   "'{container_type}' but value had type '{value_type}'\n"
                   "    value: '{value}'"
        ).format(value=value,
                 container_type=container_type.__name__,
                 value_type=type(value).__name__)
        super().__init__(message=message,
                         value=value)


class ElementCheckViolation(CheckViolation):
    def __init__(self,
                 checker,
                 value,
                 message=None):
        if message is None:
            message = ("Element check violation  Checker '{checker}'"
                       "failed when examining element: '{value}'\n"
            ).format(target=None,
                     checker=checker,
                     value=value,
                     container_type=None,
                     arg_type=type(None).__name__)
        super().__init__(message=message,
                         value=value)


class IndexedElementCheckViolation(ElementCheckViolation):
    def __init__(self,
                 target,
                 arg_name,
                 arg_contract,
                 failed_contract,
                 element_index):
        pass


class DictKeyCheckViolation(ElementCheckViolation):
    def __init__(self,
                 target,
                 arg_name,
                 arg_contract,
                 failed_contract,
                 key):
        pass


class DictValueCheckViolation(ElementCheckViolation):
    def __init__(self,
                 target,
                 arg_name,
                 arg_contract,
                 failed_contract,
                 value):
        pass


class UnionCheckViolation(CheckViolation):
    def __init__(self,
                 message_lines,
                 value):
        message_lines = ["UnionCheckViolation:"] + message_lines
        super().__init__(message="\n".join(message_lines), value=value)


# end of checkers





class SignatureViolation(ContractViolation):
    def __init__(self, *, message=None, target, arg_name, arg_checker,
                 arg_value):
        self.arg_name = arg_name
        self.arg_checker = arg_checker
        self.arg_value = arg_value
        if message is None:
            message = ("Signature check_sig failed for target function: {"
                       "target_name}\n"
                       "    failed argument: {arg_name}={arg_value}\n"
                       "    checker = {arg_checker}").format(
                arg_name=arg_name,
                target_name=target.__name__,
                arg_checker=str(arg_checker),
                arg_value=str(arg_value))
        super().__init__(message=message,
                         target=target)


class ReturnSignatureViolation(SignatureViolation):
    def __init__(self, *, message=None, target, return_checker, return_value):
        if message is None:
            message = (
            "Return signature check_sig failed for target function: {"
            "target_name}\n"
            "    failed return value: {return_value}\n"
            "    checker = {return_checker}").format(
                target_name=target.__name__,
                return_checker=str(return_checker),
                return_value=str(return_value))
        super().__init__(message=message,
                         target=target,
                         arg_name='return',
                         arg_checker=return_checker,
                         arg_value=return_value)


class SignatureError(ContractError):
    def __init__(self,
                 *,
                 message=None,
                 target,
                 arg_name,
                 arg_checker,
                 arg_value):
        self.arg_name = arg_name
        self.arg_checker = arg_checker
        self.arg_value = arg_value
        if message is None:
            message = ("Error encountered while checking signature "
                       "for target function: {target_name}\n"
                       "    failed argument: {arg_name}={arg_value}\n"
                       "    arg_checker: {arg_checker}").format(
                arg_name=arg_name,
                target_name=target.__name__,
                arg_checker=str(arg_checker),
                arg_value=str(arg_value))
        super().__init__(message=message,
                         target=target)


class ConditionViolation(ContractViolation):
    def __init__(self, *, message=None, target, args, kwargs):
        if message is None:
            message = "Condition Failed"
        super().__init__(message=message, target=target)
        self.args = args
        self.kwargs = kwargs


class PreconditionViolation(ConditionViolation):
    def __init__(self, *,
                 target,
                 condition,
                 args,
                 kwargs):
        message = ("Precondition Violation on function: {target_name}\n"
                   "    precondition function: {condition}\n"
                   "    args: {args}\n"
                   "    kwargs: {kwargs}").format(target_name=target.__name__,
                                                  condition=condition,
                                                  args=args,
                                                  kwargs=kwargs)
        self.condition = condition
        super().__init__(message=message,
                         target=target,
                         args=args,
                         kwargs=kwargs)


class PostconditionViolation(ConditionViolation):
    def __init__(self,
                 *,
                 target,
                 condition,
                 args,
                 kwargs):
        message = ("Postcondition Violation on function: {target_name}\n"
                   "    postcondition function: {condition}\n"
                   "    args: {args}\n"
                   "    kwargs: {kwargs}").format(target_name=target.__name__,
                                                  condition=condition,
                                                  args=args,
                                                  kwargs=kwargs)
        self.condition = condition
        super().__init__(message=message,
                         target=target,
                         args=args,
                         kwargs=kwargs)


class InvariantViolation(ContractViolation):
    def __init__(self, *,
                 target,
                 invariant,
                 pre_val,
                 post_val,
                 return_value,
                 args,
                 kwargs):
        self.pre_val = pre_val
        self.post_val = post_val
        self.return_value = return_value
        message = ("Invariant Violation when calling target function: "
                   "{target_name}\n"
                   "    invariant: {invariant}\n"
                   "    value before call: {pre_val}\n"
                   "    value after call: {post_val}\n"
                   "    return value: {return_value}\n"
                   "    args: {args}\n"
                   "    kwargs: {kwargs}").format(
            target_name=target.__name__,
            invariant=str(invariant),
            pre_val=str(pre_val),
            post_val=str(post_val),
            return_value=str(return_value),
            args=str(args),
            kwargs=str(kwargs))
        super().__init__(message=message, target=target)


class PreconditionError(ContractError):
    def __init__(self, *,
                 message=None,
                 condition,
                 target,
                 args,
                 kwargs):
        if message is None:
            message = ("Exception encountered while evaluating precondition "
                       "{condition} for {target_name}.\n"
                       "    args: {args}\n"
                       "    kwargs: {kwargs}\n").format(
                condition=str(condition),
                target_name=target.__name__,
                args=str(args),
                kwargs=str(kwargs))
        super().__init__(message=message, target=target)
        self.condition = condition
        self.args = args
        self.kwargs = kwargs


class PostconditionError(ContractError):
    def __init__(self, *,
                 message=None,
                 condition,
                 target,
                 args,
                 kwargs):
        if message is None:
            message = ("Exception encountered while evaluating postcondition "
                       "{condition} for {target_name}.\n"
                       "    args: {args}\n"
                       "    kwargs: {kwargs}\n").format(
                condition=str(condition),
                target_name=target.__name__,
                args=str(args),
                kwargs=str(kwargs))
        super().__init__(message=message, target=target)
        self.condition = condition
        self.args = args
        self.kwargs = kwargs


class InvariantError(ContractError):
    def __init__(self, *,
                 message=None,
                 invariant,
                 when,
                 target,
                 args,
                 kwargs):
        if message is None:
            message = ("Exception encountered while evaluating invariant "
                       "{invariant} {when} {target_name}.\n"
                       "    args: {args}\n"
                       "    kwargs: {kwargs}\n").format(
                invariant=str(invariant),
                when=when,
                target_name=target.__name__,
                args=str(args),
                kwargs=str(kwargs))
        super().__init__(message=message, target=target)
        self.args = args
        self.kwargs = kwargs

