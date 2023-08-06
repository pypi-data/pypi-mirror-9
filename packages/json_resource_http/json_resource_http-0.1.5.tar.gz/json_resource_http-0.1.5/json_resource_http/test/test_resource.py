import pytest
from json_resource import ResourceNotFound, ResourceExists, ValidationError


class JSONResourceTest(object):
    def test_insert(self, resource):
        resource.insert()

        assert 'id' in resource

    def test_insert_conflict(self, resource):
        resource.insert()

        with pytest.raises(ResourceExists):
            resource.insert()

    def test_insert_validation_error(self, invalid_resource):
        with pytest.raises(ValidationError):
            invalid_resource.save()

    def test_load(self, existing_resource):
        existing_resource.load()

        assert existing_resource['category'] == 'test'

    def test_load_does_not_exists(self, resource):
        with pytest.raises(ResourceNotFound):
            resource.load()

    def test_update(self, existing_resource):
        existing_resource['category'] = 'bla'
        existing_resource.save()

        existing_resource.load()

        assert existing_resource['category'] == 'bla'

    def test_update_does_not_exist(self, resource):
        resource['category'] = 'bla'
        with py.test.raises(ResourceNotFound):
            resource.save()

    def test_delete(self, existing_resource):
        existing_resource.delete()

        with pytest.raises(ResourceNotFound):
            existing_resource.load()

    def test_delete_does_not_exist(self, resource):
        with pytest.raises(ResourceNotFound):
            existing_resource.delete()


        resource = self.TestResource({'id': 'test'})
        resource.delete()

        self.assertRaises(
            ResourceNotFound,
            resource.load
        )

    def test_insert(self):
        resource = self.TestResource({'id': 'tast', 'foo': 'bar'})
        resource.save(insert=True)

        resource.load()

        self.assertEqual(resource['foo'], 'bar')
