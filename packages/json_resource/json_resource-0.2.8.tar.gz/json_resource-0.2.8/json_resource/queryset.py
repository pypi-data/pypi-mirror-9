import copy
import re
from gettext import gettext as _

import pymongo

from .exceptions import ResourceNotFound, ResourceExists, ValidationError


class QuerySet(object):
    """ Queryset that allows for querying, creating, updating and deleting
    of resources.

    >>> ExampleResource.objects
    QuerySet<{'id': 'test'}, {'id': 'tast'}, ....>

    >>> ExampleResource.objects.filter({'id': 'test'})
    Queryset<{'id': 'test'}>
    """
    def __init__(self, resource, start=0, end=None, sort=None, filter=None):
        self.resource = resource

        self._start = start
        self._end = end
        self._sort = sort
        self._filter = filter or {}

        self._result = None

    @property
    def collection(self):
        return self.resource.collection()

    def __len__(self):
        if self._end:
            return min(self._end - self._start, self._cursor.count())
        else:
            return self._cursor.count()

    def __getitem__(self, index):
        data = self._cursor[index]
        meta = data.pop('_meta', {})

        resource = self.resource(data)
        resource.meta = meta

        return resource

    def __setitem__(self, index, value):
        raise NotImplemented()

    def __delitem__(self, index):
        raise NotImplemented()

    def __getslice__(self, start, end):
        return self.__class__(
            self.resource, start=start, end=end, filter=self._filter,
            sort=self._sort
        )

    def __setslice__(self, index, value):
        raise NotImplemented()

    def __delslice__(self, index):
        raise NotImplemented()

    def __iter__(self):
        self._result = None
        return self

    def __repr__(self):
        content = ', '.join([resource.__repr__() for resource in self[0:3]])
        if len(self) > 3:
            content += ', ...'

        return 'QuerySet(%s)([%s])' % (self.resource.__name__, content)

    @property
    def _cursor(self):
        if not self._result:
            self._result = self.collection.find(
                self._filter, {'_id': False}
            )
            if self._sort:
                self._result.sort(self._sort)

            if self._end:
                self._result.limit(self._end)

            if self._start:
                self._result.skip(self._start)

        return self._result

    def sort(self, sort):
        result = copy.deepcopy(self)
        result._sort = sort

        return result

    def filter(self, filter):
        result = copy.deepcopy(self)
        result._filter.update(filter)

        return result

    def next(self):
        data = self._cursor.next()

        return self.resource(data, meta=data.pop('_meta'))

    def get(self, query=None):
        filter = dict(self._filter)
        if query:
            filter.update(query)

        data = self.collection.find_one(
            filter,
            fields={'_id': False}
        )

        if data is None:
            raise ResourceNotFound(filter)

        resource = self.resource(data)
        resource.meta = resource.pop('_meta')

        return resource

    def load(self, resource):
        data = self.collection.find_one(
            {'_id': resource._id}, fields={'_id': False}
        )

        if not data:
            raise ResourceNotFound(resource.url)

        resource.meta = data.pop('_meta')

        resource.update(data)

    def insert(self, resource, validate=True):
        data = dict(resource)
        data['_id'] = resource._id
        data['_meta'] = resource.meta

        try:
            self.collection.insert(data, j=True)
        except pymongo.errors.DuplicateKeyError, e:
            raise ResourceExists(resource.url)

    def save(self, resource, validate=True, upsert=True):
        data = dict(resource)
        data['_id'] = resource._id
        data['_meta'] = resource.meta

        try:
            result = self.collection.update(
                {'_id': resource._id}, data, upsert=upsert
            )
        except pymongo.errors.DuplicateKeyError, e:
            query = re.search(
                'index\: (?P<ns>[\w\-\.]+)\.\$(?P<name>\w+)', e.message
            ).groupdict()
            index = self.collection.database['system.indexes'].find_one(query)

            error = {
                'message': 'Already exists',
                'validator': 'unique',
                'path': '/' + index['key'].keys()[0]
            }
            raise ValidationError(error)

        if result['n'] == 0:
            raise ResourceNotFound(resource.url)

    def delete(self, resource):
        result = self.collection.remove({'_id': resource._id})

        if result['n'] == 0:
            raise ResourceNotFound(resource.url)
