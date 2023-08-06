import json
import json_resource

from json_resource_http.queryset import HTTPQuerySet, AuthorizedQuerySet


class HTTPResourceMeta(json_resource.StoredResourceMeta):
    """ Metaclass that add an `objects` member to the class.

    The objects member is a queryset that allows creating, querying and deleting
    resources of the class.
    """
    def __new__(cls, name, bases, dct):
        result = json_resource.ResourceMeta.__new__(cls, name, bases, dct)

        if result.schema and not hasattr(result, 'objects'):
            result.objects = result._query_set_class(
                result
            )

        return result


class Resource(json_resource.Resource):
    __metaclass__ = HTTPResourceMeta

    _query_set_class = HTTPQuerySet

    def __init__(self, data, headers=None, **kwargs):
        """ Initialize a resource.

        Adds the possibilty to add headers that will be send on every request.
        """
        self._headers = headers or {}

        super(Resource, self).__init__(data, **kwargs)

    def serialize(self):
        return json.dumps(self)

    def patch(self, patch):
        """ Patch a resource by performing a http request. These changes
        will be saved immediately
        """
        return self.objects.patch(self, patch)

    def save(self, create=False, validate=True, **kwargs):
        """ Save a resource.

        Add the possibilty to validate with a different schema when creating
        a resource.
        """
        if create:
            if validate:
                self.validate(create=True)

            validate = False

        super(Resource, self).save(create=create, validate=validate, **kwargs)

    @property
    def headers(self):
        """ Headers to be send on every request.

        By default add the correct content-type.
        """
        headers = {
            'content-type': 'application/json'
        }
        headers.update(self._headers)

        return headers


class AuthorizedResource(Resource):
    """ HTTP resource that is authorized using a bearer token.

        Send an authorization header with every request
    """
    _query_set_class = AuthorizedQuerySet
    token = None

    @property
    def headers(self):
        """ Header send when performing a request.

        Adds authorization header.
        """
        headers = super(AuthorizedResource, self).headers

        if self.token:
            headers['Authorization'] = 'Bearer %s' % self.token['access_token']

        return headers


class CachedResource(AuthorizedResource):

    @property
    def _cache_key(self, url):
        if not url:
            url = self._id

        return 'json-resource-%s-%s' % (url, self.token._id)

    def save(self, *args, **kwargs):
        super(CachedResource, self).save(*args, **kwargs)
        self.cache.delete(self._cache_key)

    def patch(self, *args, **kwargs):
        super(CachedResource, self).save(*args, **kwargs)
        self.cache.delete(self._cache_key)

    def delete(self, *args, **kwargs):
        super(CachedResource, self).save(*args, **kwargs)
        self.cache.delete(self._cache_key)

    def load(self, url=None):
        data = self.cache.get(self._cache_key(url))

        if data:
            self.update(data)
        else:
            super(CachedResource, self).load(url=url)
            self.cache.set(
                self._cache_key(url), self, timeout=self.cache_timeout
            )

        return self
