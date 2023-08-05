from ..errors.mtce import BadMultitonIdentifier as BMI


class Singleton(type):
    """The **singleton pattern** is a design pattern that restricts the
    instantiation of a class to one object. This is useful when exactly one
    object is needed to coordinate actions across the system.

    As a metaclass, the pattern is applied to derived classes such as

    ::

        from pynion import Singleton

        class Foo(object):
            __metaclass__ = Singleton

            def __init__(self, bar):
                self.bar = bar

    Derived classes can become parents of other classes. Classes inherited from
    a ``__metaclass__ = Singleton`` are also Singleton.

    """
    instance = {}

    def __call__(cls, *args, **kw):
        if cls not in cls.instance:
            cls.instance[cls] = super(Singleton, cls).__call__(*args, **kw)
        return cls.instance[cls]


class Multiton(type):
    """The **multiton pattern** is a design pattern similar to the singleton.
    The multiton pattern expands on the singleton concept to manage a map of
    named instances as key-value pairs. This means that rather than having a
    single instance per application the multiton pattern instead ensures a
    single instance per key.

    As a metaclass, the pattern is applied to derived classes through the
    :py:attr:`__metaclass__`. By default, the key attribute of the multiton is
    either:

        * the :py:meth:`__init__` named argument **name** or
        * the first argument of :py:meth:`__init__` if not named.

    The default named argument can be changed by adding the class attribute
    :py:const:`_IDENTIFIER`

    ::

        from pynion import Multiton

        class Foo(object):
            __metaclass__ = Multiton
            _IDENTIFIER   = 'newID'  # by default this will be 'name'

            def __init__(self, newID):
                self.id = newID

    Derived classes can become parents of other classes. Classes inherited from
    a ``__metaclass__ = Multiton`` are also Multiton, although their
    :py:const:`_IDENTIFIER` can be changed.
    """
    instance = {}

    def __call__(cls, *args, **kw):
        try:                   idkey = cls._IDENTIFIER
        except AttributeError: idkey = 'name'
        if kw and idkey in kw: ident = kw[idkey]
        elif len(args) > 0:    ident = args[0]
        else:                  raise BMI([idkey, cls.__name__])

        if cls not in cls.instance:
            cls.instance.setdefault(cls, {})
        if ident not in cls.instance[cls]:
            cls.instance[cls][ident] = super(Multiton, cls).__call__(*args, **kw)
        return cls.instance[cls][ident]
