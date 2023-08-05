from json_resource.instance import JSONInstance


class Integer(long, JSONInstance):
    type = (int, long)

    def __new__(cls, self=0, schema=None):
        result = long.__new__(cls, self)
        JSONInstance.__init__(result, self, schema=schema)

        return result


class Number(float, JSONInstance):
    type = (float, )

    def __new__(cls, self=0, schema=None):
        result = float.__new__(cls, self)
        JSONInstance.__init__(result, self, schema=schema)

        return result


