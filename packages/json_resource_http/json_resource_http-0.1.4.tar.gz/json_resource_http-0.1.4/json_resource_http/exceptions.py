import json
from json_resource import exceptions


class HTTPException(Exception):
    def __init__(self, response):
        self.response = response


class ServiceUnavailable(exceptions.ServiceUnavailable):
    def __init__(self, url):
        super(ServiceUnavailable, self).__init__(
            'Service Unavailable: %s' % url
        )


class InvalidResource(HTTPException):
    @property
    def message(self):
        return 'Invalid resource: %s' % self.response.request.url


class ResourceNotFound(HTTPException, exceptions.ResourceNotFound):
    @property
    def message(self):
        return 'Resource not found: %s' % self.response.request.url


class ResourceExists(HTTPException, exceptions.ResourceExists):
    @property
    def message(self):
        return 'Resource exists: %s' % self.response.request.url


class ValidationError(HTTPException, exceptions.ValidationError):
    @property
    def message(self):
        return 'Validation error: %s' % self.response.content

    @property
    def errors(self):
        return json.loads(self.response['error'])


class Forbidden(HTTPException, exceptions.Forbidden):
    @property
    def message(self):
        return 'Forbidden: %s' % self.response.request.url


class UnAuthorized(HTTPException, exceptions.UnAuthorized):
    @property
    def message(self):
        return 'UnAuthorized: %s' % self.response.request.url
