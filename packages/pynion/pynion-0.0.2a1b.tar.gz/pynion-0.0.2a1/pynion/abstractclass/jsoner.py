from abc import ABCMeta
import json

import jsonpickle

try:
    from .numpy_handlers import NPReadable
    from .numpy_handlers import register_numpy_handlers
    np_readable = NPReadable()
    register_numpy_handlers()
except:
    np_readable = None


class JSONer(object):
    """The abstract class **JSONer** adds to its descendants the required
    functions in order to export/import any given object as json. This can be
    useful to share the data between different languages or simply to store
    pre-calculated data.

    """
    __metaclass__ = ABCMeta

    def to_json(self, unpicklable = True, readable = False, api = False):
        """Export the object to a json formated string.

        :param bool unpicklable:
            When :py:data:`False` the resulting json cannot
            be reloaded as the same object again. Makes the json smaller.

        :param bool readable:
            When flattening complex object variables to json,
            this will include a human-readable version together with the stored
            json. See `jsonpickle <http://jsonpickle.github.io/>`_ on how to
            flatten and restore complex variable types. It does not affect the
            conversion of the json string into the object again.

        :param bool api:
            When flattening complex object variables to json, this
            will substitute the compressed data by the human readable version.
            Although it might allow for the conversion of the json into the
            object, some attributes will become their simplest representation.
            For example, a `numpy array <http://www.numpy.org/>`_ will be
            reloaded a a simple python array.

        :return: a json representation of the object
        :rtype: :py:data:`str`

        """
        if np_readable is not None:
            np_readable.status = readable
            np_readable.api    = api
        return jsonpickle.encode(self, unpicklable=unpicklable)

    def to_dict(self, unpicklable = True, readable = False, api = False):
        """Export the object to a json as a dictionary.

        :param bool unpicklable:
            When :py:data:`False` the resulting json cannot
            be reloaded as the same object again. Makes the json smaller.

        :param bool readable:
            When flattening complex object variables to json,
            this will include a human-readable version together with the stored
            json. See `jsonpickle <http://jsonpickle.github.io/>`_ on how to
            flatten and restore complex variable types. It does not affect the
            conversion of the json string into the object again.

        :param bool api:
            When flattening complex object variables to json, this
            will substitute the compressed data by the human readable version.
            Although it might allow for the conversion of the json into the
            object, some attributes will become their simplest representation.
            For example, a `numpy array <http://www.numpy.org/>`_ will be
            reloaded a a simple python array.

        :return: a json dictionary object
        :rtype: :py:data:`dict`

        """
        return json.loads(self.to_json(unpicklable, readable, api))

    @staticmethod
    def from_json(json_data):
        """Given a json-formated string, it recreates the object.

        :param str json_data: json-formated string.
        :return: an instance of the caller object type.
        :rtype: :py:data:`object instance`

        """
        return jsonpickle.decode(json_data)
