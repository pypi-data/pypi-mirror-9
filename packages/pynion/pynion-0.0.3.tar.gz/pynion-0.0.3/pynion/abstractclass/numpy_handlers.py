import jsonpickle
import numpy as np


from .. import Singleton

# https://github.com/hpk42/numpyson/blob/master/numpyson.py


class NPReadable(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.status = False
        self.api    = False

    def __str__(self):
        return '-'.join([str(self.status), str(self.api)])

np_readable = NPReadable()


class BaseHandler(jsonpickle.handlers.BaseHandler):
    def nrestore(self, arg, reset=False):
        return self.context.restore(arg, reset=reset)

    def nflatten(self, arg, reset=False):
        return self.context.flatten(arg, reset=reset)


class NumpyNumber(BaseHandler):
    """A jsonpickle handler for numpy floats."""
    def flatten(self, obj, data):
        data["__reduce__"] = (self.nflatten(type(obj)), [float(obj)])
        if not np_readable.api:
            return data
        else:
            return float(obj)

    def restore(self, obj):
        cls, args = obj['__reduce__']
        cls       = self.nrestore(cls)
        return cls(args[0])


class NumpyArrayHandler(BaseHandler):
    """A jsonpickle handler for numpy (de)serialising arrays."""
    def flatten(self, obj, data):
        order = 'F' if obj.flags.fortran else 'C'
        buf   = jsonpickle.util.b64encode(obj.tostring(order=order))
        shape = self.nflatten(obj.shape)
        dtype = str(obj.dtype)
        args  = [shape, dtype, buf, order]
        data['__reduce__']   = (self.nflatten(np.ndarray), args)
        if np_readable.status:
            data['__readable__'] = obj.tolist()
        if not np_readable.api:
            return data
        else:
            return obj.tolist()

    def restore(self, obj):
        cls, args = obj['__reduce__']
        cls       = self.nrestore(cls)
        shape     = self.nrestore(args[0])
        dtype     = np.dtype(self.nrestore(args[1]))
        buf       = jsonpickle.util.b64decode(args[2])
        order     = args[3]
        return cls(shape=shape, dtype=dtype, buffer=buf, order=order)


class NumpyMatrixHandler(NumpyArrayHandler):
    """A jsonpickle handler for numpy matrix."""
    def restore(self, obj):
        mtrx = super(NumpyMatrixHandler, self).restore(obj)
        return np.matrix(mtrx)


def register_numpy_handlers():
    jsonpickle.handlers.registry.register(np.float,   NumpyNumber)
    jsonpickle.handlers.registry.register(np.float32, NumpyNumber)
    jsonpickle.handlers.registry.register(np.float64, NumpyNumber)
    jsonpickle.handlers.registry.register(np.ndarray, NumpyArrayHandler)
    jsonpickle.handlers.registry.register(np.matrix,  NumpyMatrixHandler)
