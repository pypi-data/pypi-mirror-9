import unittest

from json_resource import Resource, Schema, ValidationError

from json_pointer import Pointer
from json_patch import Patch


schema = Schema({
    'id': 'test',
    'description': 'Test Description',
    'title': 'Test Title',
    'properties': {
        'id': {'type': 'number'},
        'sub-resource': {
            'properties': {
                'test': {'type': 'string'}
            }
        },
        'type': {'type': 'string'}
    },
    'required': ['id'],
    'links': [
        {
            'rel': 'self',
            'mediaType': 'application/json',
            'href': '/test/{id}'
        },
        {
            'rel': 'self',
            'mediaType': 'application/jpeg',
            'href': '/test/{id}.jpg'
        }
    ]
})


class ResourceTest(unittest.TestCase):
    def setUp(self):
        self.resource = Resource(
            {'id': 'bla', 'sub-resource': {'test': 'bla'}},
            schema=schema
        )

    def test_url(self):
        url = self.resource.url
        self.assertEqual(url, '/test/bla')

    def test_url_missing(self):
        resource = Resource({}, schema={})

        self.assertFalse(resource.rel('self'))

    def test_get_item(self):
        self.assertEqual(
            self.resource[Pointer('/id')],
            'bla'
        )

        self.assertEqual(
            self.resource['id'],
            'bla'
        )

    def test_key_subresource(self):
        sub_resource = self.resource['sub-resource']

        self.assertTrue('test' in sub_resource.schema['properties'])

        self.assertEqual(
            sub_resource['test'],
            'bla'
        )

    def test_get_subresource(self):
        sub_resource = self.resource.get('sub-resource')

        self.assertTrue('test' in sub_resource.schema['properties'])

        self.assertEqual(
            sub_resource['test'],
            'bla'
        )

    def test_validate(self):
        self.assertRaises(
            ValidationError,
            self.resource.validate,
        )

    def test_patch(self):
        patch = Patch([{'op': 'add', 'value': 'bla', 'path': '/type'}])
        self.resource.patch(patch)
        self.assertEqual(self.resource['type'], 'bla')


