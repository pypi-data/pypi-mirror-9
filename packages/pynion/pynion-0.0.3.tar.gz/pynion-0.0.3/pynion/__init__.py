"""**Pynion** is a small python minion library that provides two key features to
help both developers and python users alike:

* For **developers**, it provides a series of classes designed to help logging as well as in the control of I/O processes.

* For **users**, it provides a system to build a project's pipeline by tracking multiple python executions.

.. moduleauthor:: Jaume Bonet <jaume.bonet@gmail.com>

"""

from .metaclass     import *
from .abstractclass import *
from .main          import *
from .filesystem    import *

__version__ = '0.0.3'

__all__ = []
__all__.extend(metaclass.__all__)
__all__.extend(abstractclass.__all__)
__all__.extend(main.__all__)
__all__.extend(filesystem.__all__)
