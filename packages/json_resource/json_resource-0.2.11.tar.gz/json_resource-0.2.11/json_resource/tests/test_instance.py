import unittest

from json_resource import Object, Array, Schema


class ResourceTest(unittest.TestCase):
    def test_properties(self):
        obj = Object(
            {'test': 'example'},
            schema=Schema({'properties': {'test': {'type': 'string'}}})
        )
        self.assertEqual(obj['test'].schema, {'type': 'string'})

    def test_properties_non_matching(self):
        obj = Object(
            {'test': 'example'},
            schema=Schema({'properties': {'tast': {'type': 'string'}}})
        )
        self.assertEqual(obj['test'].schema, {})

    def test_additional_properties(self):
        obj = Object(
            {'test': 'example'},
            schema=Schema({'additionalProperties': {'type': 'string'}})
        )

        self.assertEqual(obj['test'].schema, {'type': 'string'})

    def test_items(self):
        obj = Array(
            [{'test': 1}, {'test': 2}, {'test': '3'}],
            schema=Schema({
                'items': {
                    'properties': {
                        'test': {
                            'type': 'number',
                            'pattern': '1'
                        }
                    }
                }
            })
        )

        self.assertTrue('properties' in obj[1].schema)
        self.assertEqual(obj[1]['test'].schema, {'type': 'number', 'pattern': '1'})

    def test_items_tuple(self):
        obj = Array(
            [{'test': 1}, {'test': 2}, {'test': 3}],
            schema=Schema({'items': ({'type': 'number'}, {'type': 'string'})})
        )
        self.assertEqual(obj[1].schema, {'type': 'string'})
        self.assertEqual(obj[0].schema, {'type': 'number'})

    def test_additional_items(self):
        obj = Array(
            [1, 2, 3],
            schema=Schema({
                'items': ({'type': 'number'}, {'type': 'string'}),
                'additionalItems': {'type': 'integer'}
            })
        )

        self.assertEqual(obj[0].schema, {'type': 'number'})
        self.assertEqual(obj[1].schema, {'type': 'string'})
        self.assertEqual(obj[2].schema, {'type': 'integer'})
