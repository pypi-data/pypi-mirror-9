import re
import os
import jsonschema

import json

from json_resource import Object, ResourceNotFound


class Schema(Object):
    _schema_dirs = [os.path.join(os.path.dirname(__file__), 'schemas')]
    _store = []

    @property
    def validator(self):
        return jsonschema.Draft4Validator(self)

    def load(self):
        for schema_dir in self._schema_dirs:
            try:
                with open(os.path.join(
                        schema_dir, '%s.json' % self['id']
                )) as f:
                    schema = json.load(f)
                    self.update(schema)

                    self._store.append((self.url, self))
                    return self
            except IOError:
                pass

        raise ResourceNotFound(self['id'])

    @classmethod
    def register_schema_dir(cls, dir):
        cls._schema_dirs.append(dir)

    def sub_schema(self, data, key):
        if isinstance(data, dict):
            return self._sub_schema_object(data, key)
        elif isinstance(data, (list, tuple)):
            return self._sub_schema_array(data, key)
        else:
            raise TypeError('No sub_schema available for type')

    def _sub_schema_object(self, data, key):
        sub_schema = None

        try:
            if key in self.get('properties', {}):
                sub_schema = self['properties'][key]

            for pattern, pattern_schema in self.get(
                    'patternProperties', {}).items():

                if re.findall(pattern, key):
                    if sub_schema is None:
                        sub_schema = {}

                    sub_schema.update(pattern_schema)

            if sub_schema is None and 'additionalProperties' in self:
                sub_schema = self['additionalProperties']
        except AttributeError:
            pass

        return Schema(sub_schema)

    def _sub_schema_array(self, data, index):
        sub_schema = self.get('items', {})

        if isinstance(sub_schema, (list, tuple)):
            try:
                sub_schema = sub_schema[index]
            except IndexError:
                try:
                    sub_schema = self['additionalItems']
                except KeyError:
                    sub_schema = {}

        return Schema(sub_schema)


Schema.schema = Schema(
    {'id': "schema"}
)
