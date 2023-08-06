.. include:: ../README.rst

Resources
-----------
JSON resources are subclasses of basic python classes, that can be validated and
located using json schema.

.. code-block:: python

    >>> from json_resource import Object, Schema

    >>> dict_resource = Object(
        {'test': 'bla'}, 
        schema=Schema({
            'properties': {'test': {'type': 'string'},
            'links': [{'href': '/resource/{test}/', 'rel': 'self'}]
        })
    )

    >>> dict_resource.url
    /resource/bla/


Validation
-----------

.. code-block:: python

    >>> dict_resource.validate()

    >>> dict_resource['test'] = 1
    >>> dict_resource.validate()
    Exception: '/test' should be of type string


JSON-pointer
--------------

Resources suppert indexing by json-pointer

.. code-block:: python

    >>> from json_pointer import Pointer
    >>> pointer = Pointer('/list/1')
    >>> resource[pointer]
    4 

JSON-patch
----------

Resources can be modified using json-patch

.. code-block:: python

    >>> from json_patch import Patch
    >>> patch = [{'op': 'add': 'path': '/list/4', 'value': 6}]
    >>> resource.patch(patch)
    >>> resource['list']
    [3,4,5,6]

Sub-resources
--------------


When possible indexing returns another json resource:

.. code-block:: python

    >>> dict_resource['test'].schema
    {'type': 'string'}
    >>> dict_resource['test'].validate()
    Exception: '/' should be of type string


    >>> dict_resource['test'].schema
    {'type': 'string'}
    >>> dict_resource['test'].validate()
    Exception: '/' should be of type string


Storing Resource
----------------

`Stored Resources` can be stored in a mongo database:

.. code-block:: python

    >>> from json_resource import StoredResource, Schema

    >>> class ExampleResource(StoredResource):
            schema = Schema({
                'properties': {'id': {'type': 'string'},
                'required': 'id',
                'links': [{'rel': 'self', 'href': '/test/{id}
            })
            collection = pymongo.connection()['example']

    >>> example = Example({'id': 'test', 'tags': [1,2,3])
    >>> example.exists
    False
    >>> example.save()
    >>> example.exists
    True
    >>> Example({'id': 'test'}).load()
    {'id': 'test', 'tags': [1,2,3]}
    >>> Example.objects
    QuerySet[Example]<{'id': 'test', 'tags': [1,2,3]}>
    >>> Example.objects.filter({'id': 'tast'})
    QuerySet[Example]<>

    >>> Example({'id': 'tast'}).load()
    Exception: Resource not found: /resource/tast/

