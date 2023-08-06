import json
import requests

from json_resource_http.exceptions import (
    ResourceNotFound, ResourceExists, Forbidden, UnAuthorized, InvalidResource,
    ValidationError, ServiceUnavailable
)


class HTTPQuerySet(object):
    def __init__(self, resource, **kwargs):
        self.resource = resource
        self._result = None

    def __len__(self):
        return len(self._result)

    def _reset(self):
        self._result = None

    def _exception(self, response):
        if response.status_code == 404:
            raise ResourceNotFound(response)
        elif response.status_code == 409:
            raise ResourceExists(response)
        elif response.status_code == 401:
            raise UnAuthorized(response)
        elif response.status_code == 403:
            raise Forbidden(response)
        elif response.status_code == 422:
            raise ValidationError(
                json.loads(response.content)
            )
        else:
            raise InvalidResource(response)

    def next(self):
        if not self._result:
            self._result = requests.get(self.resource().rel('collection'))

        return self._resource(self._result.next())

    def do_request(self, method, url, resource, **kwargs):
        try:
            response = requests.request(
                method,
                url,
                headers=resource.headers,
                **kwargs
            )
        except requests.ConnectionError:
            raise ServiceUnavailable(url)

        if response.status_code not in (200, 201, 204):
            raise self._exception(response)

        if response.content:
            try:
                return json.loads(response.content)
            except ValueError:
                raise InvalidResource(response)

    def load(self, resource, url=None):
        url = url or resource.url

        data = self.do_request('get', url, resource)
        resource.update(data)

    def insert(self, resource, validate=True):
        data = self.do_request(
            'post',
            resource.rel('create'),
            resource,
            data=resource.serialize()
        )
        resource.clear()
        resource.update(data)

    def save(self, resource, validate=True, upsert=True):
        self.do_request(
            'put',
            resource.url,
            resource,
            data=resource.serialize()
        )

    def patch(self, resource, patch):
        data = self.do_request(
            'patch',
            resource.url,
            resource,
            data=json.dumps(patch)
        )

        resource.clear()
        resource.update(data)

    def delete(self, resource):
        self.do_request(
            'delete',
            resource.url,
            resource
        )


class AuthorizedQuerySet(HTTPQuerySet):
    def do_request(self, method, url, resource, **kwargs):
        try:
            return super(AuthorizedQuerySet, self).do_request(
                method, url, resource, **kwargs
            )
        except UnAuthorized:
            if resource.token and resource.token.refresh():
                return super(AuthorizedQuerySet, self).do_request(
                    method, url, resource, **kwargs
                )
            else:
                raise
