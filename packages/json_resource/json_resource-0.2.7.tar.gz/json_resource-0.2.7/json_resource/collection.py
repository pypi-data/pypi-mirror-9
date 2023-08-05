from json_resource import Object
from json_resource.store import StoredResourceMeta


class Collection(Object):
    __metaclass__ = StoredResourceMeta
    queryset = None

    meta = {}
    default_meta = {
        'page_size': 10,
        'page': 1,
    }

    def __init__(self, data=None):
        if data is None:
            data = {}

        data['meta'] = dict(self.default_meta)
        data['meta'].update(data.get('meta', {}))

        super(Collection, self).__init__(data)

    def load(self):
        page = int(self['meta']['page'])
        page_size = int(self['meta']['page_size'])

        filter = dict([(key, value) for key, value in self.items()
                      if key not in ('items', 'meta')])

        self['items'] = list(
            self.objects.filter(filter)[(page - 1) * page_size:page * page_size]
        )
        self['meta']['found'] = len(self.objects)

        return self
