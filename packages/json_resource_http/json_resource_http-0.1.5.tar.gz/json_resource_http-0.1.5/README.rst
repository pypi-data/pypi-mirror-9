JSON Resource HTTP
=============

HTTP queryset backend for json resources. Makes it possible to use json-schema
api's as if they were local.


Installation
------------

pip install json_resource_http


Minimal Example
-------------------

.. code-block:: python

    from json_resource_http import Resource

    class TestResource(Resource):
        schema = 'http://example.com/schemas/test.json'



