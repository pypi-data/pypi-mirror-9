class Switch:
    """
    This class implements a simple switch interface.  An instance can be
    turned enabled or disabled.

    A Switch can function as a master for any number of other Switches.
    This allows a single switch to control any number of other Switches.
    If a switch is slaved to another Switch instance, it gets the value of
    its `enabled` property from its master.  The master switch is set using
    the 'master' attribute.  If a switch is slaved to another, its 'enabled'
    property becomes read-only.
    """

    def __init__(self, *, enabled=True, master=None):
        """
        :param enabled: is this Switch enabled?
        :type enabled: bool
        :param master: the master Switch to slave this instance to.
        :type master: Switch or None
        """
        self._master = master
        self._enabled = enabled

    @property
    def enabled(self):
        """
        Enable this Switch by setting enabled=True.  Disable this Switch
        by setting enabled = False.  If this Switch is slaved to another
        Switch, its `enabled` property cannot be set.
        """
        if self._master is None:
            return self._enabled
        return self.master.enabled

    @enabled.setter
    def enabled(self, new_value):
        if self._master is not None:
            raise AttributeError("This Switch is slaved to another Switch."
                                 "The enabled property can only be set "
                                 "through the master switch.")
        if not isinstance(new_value, bool):
            raise ValueError("enabled can only be set to a boolean value")
        self._enabled = new_value

    @property
    def master(self):
        return self._master

    @master.setter
    def master(self, new_master):
        if new_master is None:
            if self._master is not None:
                self._enabled = self._master.enabled
            self._master = None
        elif hasattr(new_master, 'enabled'):
            self._master = new_master
        else:
            raise ValueError("The master attribute must be set to None or an "
                             "object that has an 'enabled' property.")

    def __str__(self):
        return "Switch(enabled=%s, master=%s)" % (self.enabled, self.master)


