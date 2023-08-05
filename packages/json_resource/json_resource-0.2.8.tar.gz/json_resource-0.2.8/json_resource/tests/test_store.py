import unittest
import os

from pymongo import MongoClient

from json_resource import Resource, Schema, ResourceNotFound, ResourceExists, \
    ValidationError


Schema.register_schema_dir(
    os.path.join(os.path.dirname(__file__), 'schemas')
)


class StoredTestResource(Resource):
    schema = Schema({'id': 'stored-test'})

    @classmethod
    def db(cls):
        return MongoClient()['test']


class StoredResourceTest(unittest.TestCase):
    def setUp(self):
        self.resource = StoredTestResource({'id': 1})

    def tearDown(self):
        StoredTestResource.objects.collection.remove({})

    def test_insert(self):
        self.resource.save(create=True)

        self.assertTrue(self.resource.exists)

    def test_insert_exists(self):
        self.resource.save(create=True)

        self.assertRaises(
            ResourceExists,
            self.resource.save,
            create=True
        )

    def test_load(self):
        self.resource['test'] = 'bla'

        self.resource.save()

        resource = StoredTestResource({'id': 1})
        resource.load()

        self.assertEqual(resource['test'], 'bla')

    def test_load_does_not_exists(self):
        self.assertRaises(
            ResourceNotFound,
            StoredTestResource({'id': 2}).load
        )

    def test_insert_invalid(self):
        self.resource['id'] = 'bla'

        self.assertRaises(
            ValidationError,
            self.resource.save,
        )

        self.assertFalse(self.resource.exists)

    def test_save(self):
        self.resource.save()

        self.assertTrue(self.resource.exists)

    def test_save_invalid(self):
        self.resource['id'] = 'bla'

        self.assertRaises(
            ValidationError,
            self.resource.save,
        )
        self.assertFalse(self.resource.exists)

    def test_save_no_upsert(self):
        self.assertRaises(
            ResourceNotFound,
            self.resource.save,
            upsert=False
        )

    def test_delete(self):
        self.resource.save()

        self.resource.delete()
        self.assertFalse(self.resource.exists)

    def test_delete_does_not_exists(self):
        self.assertRaises(
            ResourceNotFound,
            self.resource.delete
        )

