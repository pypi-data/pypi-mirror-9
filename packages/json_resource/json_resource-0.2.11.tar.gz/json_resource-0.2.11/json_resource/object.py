import re

from json_resource.instance import JSONInstance
from json_pointer import Pointer


class Object(JSONInstance, dict):
    """ Object resource. This is a subclass of `dict` that can be validated using
    a schema.
    """
    type = (dict, )

    def __init__(self, data=None, schema=None):
        if data is None:
            data = {}

        JSONInstance.__init__(self, data, schema=schema)
        dict.__init__(self, data)

    def __getitem__(self, key):
        """ Override __getitem__ so that it accepts json pointers.

        When a subschema is available, the returned object is a resource that
        also has a schema.
        """
        if isinstance(key, Pointer):
            return key.get(self)
        else:
            result = dict.__getitem__(self, key)

            if not isinstance(result, JSONInstance):
                result = JSONInstance.load(result, schema=self._sub_schema(key))
                self[key] = result

            return result

    def __setitem__(self, key, value):
        """ Override __getitem__ so that it accepts json pointers.

        When a subschema is available, the returned object is a resource that
        also has a schema.
        """
        if isinstance(key, Pointer):
            key.set(self, value)
        else:
            super(Object, self).__setitem__(key, value)

    def get(self, key, default=None):
        """ Override `get` to accept json pointers.

        When a subschema is available, the returned object is a resource that
        also has a schema.
        """
        try:
            if isinstance(key, Pointer):
                return key.get(self, default)
            else:
                result = dict.__getitem__(self, key)
                return JSONInstance.load(result, schema=self._sub_schema(key))
        except KeyError:
            return default

    def items(self):
        return [(key, JSONInstance.load(value, schema=self._sub_schema(key))) for
                key, value in dict.items(self)]

    def values(self):
        return [JSONInstance.load(value, schema=self._sub_schema(key)) for
                key, value in dict.items(self)]

    def _sub_schema(self, key):
        """Returns the schema of the item under `key`."""
        try:
            return self.schema.sub_schema(self, key)
        except AttributeError:
            return None
