import unittest

from code_climate import models, exceptions
from tests.unit.tests_models import ModelTestMixin


class TestModelOrganization(ModelTestMixin, unittest.TestCase):
    @property
    def sample_name(self):
        return 'orgs'

    def test_fields(self):
        data = self.samples[0]
        organization = models.Organization(data=data)

        self.assertEqual('58da767f6261830264001e69', organization.id)
        self.assertEqual("joaodaher", organization.name)

    def test_fields_repositories(self):
        data = self.samples[0]
        organization = models.Organization(data=data)

        repository_data = [{'id': 10}, {'id': 20}]
        with self.patch_get(data=repository_data) as get:
            repositories = list(organization.repositories)

        self.assertEqual(2, len(repositories))
        [repo_a, repo_b] = repositories
        self.assertEqual(10, repo_a.id)
        self.assertEqual(20, repo_b.id)

        self.assertPaginated(
            patched=get,
            resource='repos',
            id=organization.id,
            from_resource='orgs',
            number_of_pages=3,
        )

    def test_invalid_field(self):
        organization = models.Organization(data={})
        with self.assertRaises(exceptions.UnexpectedDataFormat):
            organization.name  # pylint: disable=pointless-statement

    def test_list(self):
        data = self.samples
        with self.patch_get(data=data) as get:
            organizations_iter = models.Organization.list()

            organizations = list(organizations_iter)
            self.assertEqual(2, len(organizations))

            [organization_a, organization_b] = organizations
            sample_a, sample_b = self.samples
            self.assertEqual(sample_a, organization_a._data)
            self.assertEqual(sample_b, organization_b._data)

        self.assertPaginated(patched=get, resource='orgs', number_of_pages=3)

    def test_detail(self):
        data = self.samples[0]
        with self.patch_get(data=data) as get:
            organization = models.Organization.get(id=42)

            sample = self.samples[0]
            self.assertEqual(sample, organization._data)

        get.assert_called_once_with(resource='orgs', id=42)

    def test_not_found(self):
        with self.patch_get_error(status_code=404) as get:
            with self.assertRaises(exceptions.DoesNotExist):
                models.Organization.get(id=666)

        self.assertEqual(1, get.call_count)
