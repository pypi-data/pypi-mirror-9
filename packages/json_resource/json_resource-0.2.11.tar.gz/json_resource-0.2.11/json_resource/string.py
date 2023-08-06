
from json_resource.instance import JSONInstance


class String(unicode, JSONInstance):
    type = (str, unicode)

    def __new__(cls, self='', schema=None):
        result = unicode.__new__(cls, self)

        return result


