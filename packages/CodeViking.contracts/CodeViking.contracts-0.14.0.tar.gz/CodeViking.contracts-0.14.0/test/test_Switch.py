import pytest

from codeviking.contracts.switch import Switch


class AA:
    def __init__(self):
        self.enabled = True


class BB:
    pass


def set_master(s, m):
    s.master = m


def set_enabled(s, e):
    s.enabled = e


def test_independent():
    a = Switch()
    a.enabled = True
    assert (a.enabled is True)

    a.enabled = False
    assert (a.enabled is False)
    assert (a.master is None)


def test_slaved():
    a = Switch()
    b = Switch(master=a)
    c = Switch(master=a)
    d = Switch(master=c)

    assert (a.master is None)

    a.enabled = True
    assert (a.enabled is True)
    assert (b.enabled is True)
    assert (c.enabled is True)
    assert (d.enabled is True)

    a.enabled = False
    assert (a.enabled is False)
    assert (b.enabled is False)
    assert (c.enabled is False)
    assert (d.enabled is False)

    pytest.raises(AttributeError, set_enabled, d, True)

    d.master = None
    assert (d.enabled is False)
    a.enabled = True
    assert (d.enabled is False)

    pytest.raises(AttributeError, set_enabled, b, False)


def test_non_switch_master():
    aa = AA()
    aa.enabled = True
    print("hasattr(aa,'enabled') = " + str(hasattr(aa, 'enabled')))

    a = Switch()
    print(a.master)
    a.master = aa
    assert (aa.enabled is True)
    assert (a.enabled is True)

    aa.enabled = False
    assert (aa.enabled is False)
    assert (a.enabled is False)


def test_bad_values():
    a = Switch()
    bb = BB()
    pytest.raises(ValueError, set_master, a, bb)
    pytest.raises(ValueError, set_enabled, a, 7)


def test_set_enabled_with_master():
    a = Switch()
    b = Switch(master=a)

    def f():
        b.enabled = False

    pytest.raises(AttributeError, f)


def test_set_enabled_non_boolean():
    a = Switch()

    def f():
        a.enabled = 1

    pytest.raises(ValueError, f)


# noinspection PyPep8Naming
def all_Switch_tests():
    test_bad_values()
    test_independent()
    test_non_switch_master()
    test_set_enabled_non_boolean()
    test_set_enabled_with_master()
    test_slaved()
