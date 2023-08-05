from json_resource import Object, ResourceMeta
from json_resource.queryset import QuerySet


class StoredResourceMeta(ResourceMeta):
    """ Metaclass that add an `objects` member to the class.

    The objects member is a queryset that allows creating, querying and deleting
    resources of the class.
    """
    def __new__(cls, name, bases, dct):
        result = super(StoredResourceMeta, cls).__new__(cls, name, bases, dct)

        if result.schema and getattr(result, 'objects', None) is None:
            result.objects = QuerySet(
                result
            )

        return result


class Resource(Object):
    __metaclass__ = StoredResourceMeta
    indexes = []

    def __init__(self, *args, **kwargs):
        self.meta = kwargs.pop('meta', {})

        super(Resource, self).__init__(*args, **kwargs)

    @property
    def _id(self):
        """ Return an id that is used for storing the resource.
        """
        return self.url

    @classmethod
    def collection(cls):
        """ Return the collection in which the resources are saved.
        """
        return cls.db()[cls.schema['id']]

    def load(self, **kwargs):
        """ Load the resource from the database.

        The resource has to contain enough data to create the `_id`

        >>> ExampleResource({'id': 'test'}).load()
        {'id': 'test', 'tags': [1, 2, 3]}
        """
        self.objects.load(self, **kwargs)

        return self

    def save(self, validate=True, upsert=True, create=False, **kwargs):
        """ Saves a resource to the database.

        If `validate` is True, make sure the resource is valid according to the
        schema

        If `upsert` is True, create the item if it does not exist

        If `create` is True, create the item, and raise an exception if that fails
        """
        if validate:
            self.validate()

        if create:
            self.objects.insert(self, validate=validate, **kwargs)
        else:
            self.objects.save(self, validate=validate, upsert=upsert, **kwargs)

    def delete(self, **kwargs):
        """ Delete the resource from the database."""
        self.objects.delete(self)

    @property
    def exists(self):
        """ Check if the resource exists.
        """
        data = self.collection().find_one({'_id': self.url})

        if not data:
            return False
        else:
            return True

    @classmethod
    def indexes(cls):
        for prop in cls.schema.get('unique', []):
            yield prop, {'unique': True}

        for prop in cls.schema.get('indexes', []):
            yield prop, {}

    @classmethod
    def ensure_indexes(cls, background=True):
        for prop, args in cls.indexes():
            cls.collection().ensure_index(
                prop,
                background=background,
                **args
            )
