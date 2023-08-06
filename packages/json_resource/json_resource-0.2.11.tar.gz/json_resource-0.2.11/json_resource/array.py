from json_pointer import Pointer

from json_resource.instance import JSONInstance


class Array(JSONInstance, list):
    """ Array resource. This is a subclass of `list` that can be validated using
    a schema.
    """
    type = (list, tuple)

    def __init__(self, data=None, schema=None):

        if data is None:
            data= []

        JSONInstance.__init__(self, schema=schema)
        list.__init__(self, data)

    def __iter__(self):
        for index, value in enumerate(list.__iter__(self)):
            yield JSONInstance.load(value, schema=self._sub_schema(index))

    def __getitem__(self, index):
        if isinstance(index, Pointer):
            return index.get(self)
        else:
            result = list.__getitem__(self, index)
            if not isinstance(result, JSONInstance):
                result = JSONInstance.load(result, self._sub_schema(index))
                self[index] = result

            return result

    def _sub_schema(self, key):
        try:
            return self.schema.sub_schema(self, key)
        except AttributeError:
            return None

