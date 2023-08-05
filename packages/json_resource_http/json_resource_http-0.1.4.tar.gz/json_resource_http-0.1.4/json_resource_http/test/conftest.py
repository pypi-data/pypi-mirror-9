import urlparse
import multiprocessing
import pytest

from flask_json_resource import API
from flask.ext.pymongo import PyMongo
from flask import Application

from json_resource_http import Resource


@pytest.fixture
def api():
    return API(__name__)


@pytest.fixture
def mongo_resource_cls(api):
    @api.register()
    class TestResource(api.Resource):
        id = 'test.json'

    def worker(api, port):
        api.run('127.0.0.1', port=port)


@pytest.yield_fixture
def server(api):
    app = Application(__name__)
    db = PyMongo()

    api.init_app(app, db)

    def worker(api, port):
        api.run('127.0.0.1', port=port)

    _process = multiprocessing.Process(
        target=worker, args=(api, 8002)
    )

    _process.start()

    yield app

    _process.terminate()


@pytest.fixture()
def resource(mongo_resource_cls):
    class TestResource(Resource):
        schema = urlparse.urljoin(
            'http://localhost:8002', mongo_resource_cls.schema.url
        )

    return TestResource({'category': 'test'})










