import os
import unittest


from pymongo import MongoClient
from json_resource import Resource, Collection, Schema


Schema.register_schema_dir(
    os.path.join(os.path.dirname(__file__), 'schemas')
)


class TestResource(Resource):
    schema = Schema({'id': 'stored-test'})

    @classmethod
    def db(cls):
        return MongoClient()['test']


class TestCollection(Collection):
    schema = Schema({'id': 'collection'})
    objects = TestResource.objects


class CollectionTest(unittest.TestCase):
    def setUp(self):
        for i in range(30):
            TestResource({'id': i}).save()

    def test_load(self):
        collection = TestCollection()
        collection.load()

        self.assertTrue(isinstance(collection['items'], list))

    def test_page_size(self):
        collection = TestCollection()
        collection['meta']['page_size'] = 3
        collection.load()

        self.assertEqual(len(collection['items']), 3)

    def test_filter(self):
        collection = TestCollection({'id': 3})
        collection.load()

        self.assertEqual(len(collection['items']), 1)
        self.assertEqual(collection['items'][0]['id'], 3)


class CollectionItemsTest(unittest.TestCase):
    def setUp(self):
        for i in range(30):
            TestResource({'id': i}).save()

        self.items = TestCollection().objects

    def test_len(self):
        self.assertEqual(len(self.items), 30)

    def test_indexation(self):
        resource = self.items[10]

        self.assertTrue('id' in resource)
        self.assertEqual(len(resource.keys()), 1)

        self.assertTrue(isinstance(resource, TestResource))

    def test_indexation_slice(self):
        self.assertEqual(len(self.items[0:10]), 10)
        for resource in self.items[0:10]:
            self.assertTrue(isinstance(resource, TestResource))

    def test_indexation_slice_start(self):
        self.assertEqual(len(self.items[5:10]), 5)
        for resource in self.items[5:10]:
            self.assertTrue(isinstance(resource, TestResource))

    def test_iteration(self):
        found = []
        for resource in self.items:
            self.assertTrue('id' in resource)
            self.assertTrue(resource not in found)
            self.assertTrue(isinstance(resource, TestResource))

            found.append(resource)

        self.assertEqual(len(found), 30)

    def test_sort(self):
        sorted = range(30)

        ids = [
            resource['id'] for resource in self.items.sort([('id', 1)])
        ]

        self.assertEqual(sorted, ids)

    def test_repr(self):
        self.assertTrue(
            self.items.__repr__().startswith(
                "QuerySet(TestResource)([{u'id':"
            )
        )
