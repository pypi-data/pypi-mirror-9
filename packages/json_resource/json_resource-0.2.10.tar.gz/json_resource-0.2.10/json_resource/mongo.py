import re
import pymongo

from json_resource import QuerySet, ResourceNotFound, ResourceExists


class MongoQuerySet(QuerySet):
    def __init__(self, resource, limit=None, offset=0,
                 filter=None, sort=None, exclude=None):
        super(MongoQuerySet, self).__init__(
            resource, limit, offset, filter, sort, exclude
        )

        self._result = None

    def ensure_indexes(self):
        for link in self.resource.schema.get('links', []):
            args = re.findall("\{(\w*)\}", link['href'])
            self.collection.ensure_index(
                [(arg, pymongo.ASCENDING) for arg in
                 args]
            )

        for index in self.resource.schema.get('indexes', []):
            self.collection.ensure_index(
                [(field, pymongo.ASCENDING) for field in index]
            )

    @property
    def collection(self):
        try:
            return self.db[self.resource.schema['id']]
        except KeyError:
            return self.db[self.resource.__class__.__name__]

    @property
    def _fields(self):
        fields = dict((field, False) for field in self._exclude)
        fields['_id'] = False

        return fields

    @property
    def _cursor(self):
        filter = self._filter

        if not self._result:
            self._result = self.collection.find(filter, self._fields)

            if self._sort:
                self._result.sort(self._sort)

            if self._limit:
                self._result.limit(self._limit)

            if self._offset:
                self._result.skip(self._offset)

        return self._result

    def __len__(self):
        if self._limit:
            return min(
                self._cursor.count() - self._offset,
                self._limit
            )
        else:
            return self._cursor.count() - self._offset

    def _resource(self, data):
        if '_id' in data:
            del data['_id']

        resource = self.resource(data)
        resource.meta = resource.pop('_meta')

        return resource

    def _reset(self):
        self._result = None

    def _meta_filter(self, filter):
        return dict([('_meta.%s' % f['field'], f['value']) for f in filter])

    def _meta_filter_failed(self, filter, url):
        resource = self.get(url)

        for f in filter:
            if resource.meta[f['field']] != f['value']:
                raise f['raises']

    def next(self):
        return self._resource(self._cursor.next())

    def get(self, url, filter=None):
        if filter is None:
            filter = []

        spec = {'_id': url}
        spec.update(self._meta_filter(filter))

        data = self.collection.find_one(
            spec,
            self._fields
        )

        if not data:
            if filter:
                self._meta_filter_failed(filter, url)

            raise ResourceNotFound()

        return self._resource(data)

    def insert(self, resource):

        resource['_id'] = resource.url
        resource['_meta'] = resource.meta

        try:
            self.collection.insert(resource, j=True)
        except pymongo.errors.DuplicateKeyError, error:
            raise ResourceExists(error)

        del resource['_id']
        del resource['_meta']

    def save(self, resource, filter=None):
        if filter is None:
            filter = []

        resource['_id'] = resource.url

        spec = {'_id': resource.url}

        spec.update(self._filter)
        spec.update(self._meta_filter(filter))

        resource['_meta'] = resource.meta

        try:
            result = self.collection.update(
                spec, resource, j=True
            )
        except pymongo.errors.DuplicateKeyError:
            raise ResourceExists(resource.url)

        if result['n'] != 1:
            if filter:
                self._meta_filter_failed(filter, resource.url)
            else:
                raise ResourceNotFound(resource.url)

        resource.meta = resource.pop('_meta')
        del resource['_id']

    def delete(self, resource, filter=None):
        if filter is None:
            filter = []

        spec = {'_id': resource.url}
        spec.update(self._meta_filter(filter))

        result = self.collection.remove(
            spec,
            j=True
        )

        if result['n'] != 1:
            if filter:
                self._meta_filter_failed(filter, resource.url)
            else:
                raise ResourceNotFound(resource.url)
