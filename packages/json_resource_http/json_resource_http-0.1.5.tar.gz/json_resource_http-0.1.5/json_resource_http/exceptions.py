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
    def __str__(self):
        return 'Invalid resource: %s (%s)' % (
            self.response.request.url, self.response.content
        )


class ResourceNotFound(HTTPException, exceptions.ResourceNotFound):
    def __str__(self):
        return 'Resource not found: %s' % self.response.request.url


class ResourceExists(HTTPException, exceptions.ResourceExists):
    def __str__(self):
        return 'Resource exists: %s' % self.response.request.url


class ValidationError(HTTPException, exceptions.ValidationError):
    def __str__(self):
        return 'Validation error: %s' % self.response.content

    @property
    def errors(self):
        return json.loads(self.response['error'])


class Forbidden(HTTPException, exceptions.Forbidden):
    def __str__(self):
        return 'Forbidden: %s' % self.response.request.url


class UnAuthorized(HTTPException, exceptions.UnAuthorized):
    def __str__(self):
        return 'UnAuthorized: %s' % self.response.request.url
