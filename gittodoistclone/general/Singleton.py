from types import MethodType


class Singleton(object):
    """
    Base class for singleton classes.

    Any class derived from this one is a singleton. You can call its
    constructor multiple times, you will get only one instance.

    Note that `__init__` must not be defined. Use `init` instead.
    This is because `__init__` will always be called, thus reinitializing the
    state of your singleton each time you try to instantiate it.
    This implementation will only call `init` a single time

    To ensure that the `__init__` method is  defined,
    the singleton checks for its existence at first instantiation and raises an
    `AssertionError` if it finds it.

    Example::

        # This class is OK
        class NoInitClass(Singleton):
            def init(self, val):
                self.val = val

        # This class will raise AssertionError at first instantiation, because
        # of the __init__ method.
        class HasInitClass(Singleton):
            def __init__(self, val):
                self.val = val
    """
    def __new__(cls, *args, **kwds):
        """
        New operator for this base singleton class.
        Will return the singleton instance or create it if needed.
        """
        instance = cls.__dict__.get("__instance__")
        if instance is None:
            instance = object.__new__(cls)
            assert type(instance.__init__) != MethodType, f"Error, your singleton class {cls} cannot contain an '__init__' method."
            try:
                instance.init(*args, **kwds)
            except Exception as e:
                raise e
            cls.__instance__ = instance
        return instance

    def init(self, *args, **kwds):
        """
        Constructor for a singleton class
        """
        pass
