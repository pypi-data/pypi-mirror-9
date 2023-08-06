import json

import requests

from json_resource import Schema


class RemoteSchema(Schema):
    def __init__(self, url):
        schema = json.loads(requests.get(url).content)

        super(RemoteSchema, self).__init__(schema, base_url=url)
