from collections import namedtuple

FuncCall = namedtuple('FuncCall', 'func args kwargs')
from .switch import Switch


class SwitchedDecorator(Switch):
    def __init__(self, wrapper, *, enabled=True, master=None, takes_args=False):
        super().__init__(enabled=enabled, master=master)
        self._wrapper = wrapper
        self._takes_args = takes_args

    def __call__(self, *args, **kwargs):
        """
        If this instance is enabled, wrap `wrapper` around `target` and
        return the result.
        If not enabled, return `target` (i.e. do not wrap `target`)
        :param target: The function to wrap.
        """
        if self._takes_args:
            if self.enabled:
                wrapper = self._wrapper(*args, **kwargs)
                return wrapper
            else:
                def identity(target):
                    return target

                return identity
        else:
            target = args[0]
            if self.enabled:
                return self._wrapper(target)
            return target


class DecoratorGroup(Switch):
    """
    A class that builds decorators from a dict of decorator definitions.

    Each named decorator is only built once.  The decorators are retrieved as
    attributes of the DecoratorGroup.
    """

    def __init__(self,
                 decorator_defs,
                 *,
                 enabled=True,
                 master=None):
        """
        A decorator definition:
            name: ((create_func),
                   args to pass to create_func,
                   kwargs to pass to create_func)

        :param decorator_defs: decorator definitions
        :type decorator_defs: dict[str, ((*,**)->T, tuple, dict)]
        :param master: the master switch to slave this DecoratorGroup to
        :type master: Switch|None
        """
        super().__init__(enabled=enabled,
                         master=master)

        self._decorator_defs = dict()
        self._decorators = dict()

        for (d_name, d_def) in decorator_defs.items():
            self._decorators[d_name] = None
            self._decorator_defs[d_name] = d_def

    def _make_dec(self, dec_func):
        return SwitchedDecorator(dec_func, master=self)

    def __getattr__(self, decorator_name):
        if decorator_name not in self._decorators:
            raise AttributeError("there is no decorator definition for "
                                 "'%s'." % decorator_name)
        if self._decorators[decorator_name] is None:
            f = self._decorator_defs[decorator_name]
            self._decorators[decorator_name] = self._make_dec(f)
        return self._decorators[decorator_name]

