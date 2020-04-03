import unittest
from datetime import datetime, timezone

from code_climate import models, exceptions
from tests.unit.tests_models import ModelTestMixin


class TestModelRepository(ModelTestMixin, unittest.TestCase):
    @property
    def sample_name(self):
        return 'repos'

    def test_fields(self):
        data = self.samples[0]
        repository = models.Repository(data=data)

        self.assertEqual('900a76232df2736347000001', repository.id)
        self.assertEqual(3385, repository.analysis_version)
        self.assertEqual('18096d266f46d9c98dd8', repository.badge_token)
        self.assertEqual('master', repository.branch)

        created_at = datetime(2018, 10, 15, 20, 8, 3, 732000, tzinfo=timezone.utc)
        self.assertEqual(created_at, repository.created_at)

        self.assertEqual("twinpeaks/potato", repository.github_slug)
        self.assertEqual("potato", repository.human_name)

        activity_at = datetime(2019, 10, 15, 20, 9, 41, 846000, tzinfo=timezone.utc)
        self.assertEqual(activity_at, repository.last_activity_at)

        self.assertEqual("76872388", repository.vcs_database_id)
        self.assertEqual("https://github.com", repository.vcs_host)
        self.assertEqual(3.14, repository.score)

    def test_fields_test_reports(self):
        data = self.samples[0]
        repository = models.Repository(data=data)

        report_data = [{'id': 10}, {'id': 20}]
        with self.patch_get(data=report_data) as get:
            reports = list(repository.test_reports)

        self.assertEqual(2, len(reports))
        [report_a, report_b] = reports
        self.assertEqual(10, report_a.id)
        self.assertEqual(20, report_b.id)

        self.assertPaginated(
            patched=get,
            resource='test_reports.json',
            id=repository.id,
            from_resource='repos',
            number_of_pages=3,
        )

    def test_invalid_field(self):
        repository = models.Repository(data={})
        with self.assertRaises(exceptions.UnexpectedDataFormat):
            repository.github_slug  # pylint: disable=pointless-statement

    def test_list(self):
        data = self.samples
        with self.patch_get(data=data) as get:
            with self.assertRaises(exceptions.UnsupportedModelException):
                models.Repository.list()

        get.assert_not_called()

    def test_find_by_slug(self):
        item = self.samples[0]
        with self.patch_get(data=[item]) as get:
            repository = models.Repository.find(github_slug='twinpeaks/potato')

            self.assertEqual(item, repository._data)

        get.assert_called_once_with(
            resource='repos',
            from_resource=None,
            id=None,
            params={'github_slug': 'twinpeaks/potato', 'page[number]': 1, 'page[size]': 100},
        )

    def test_find_by_slug_not_found(self):
        with self.patch_get(data=[]) as get:
            with self.assertRaises(exceptions.DoesNotExist):
                models.Repository.find(github_slug='twinpeaks/potato')

        get.assert_called_once_with(
            resource='repos',
            from_resource=None,
            id=None,
            params={'github_slug': 'twinpeaks/potato', 'page[number]': 1, 'page[size]': 100},
        )

    def test_detail(self):
        data = self.samples[0]
        with self.patch_get(data=data) as get:
            repository = models.Repository.get(id=42)

            sample = self.samples[0]
            self.assertEqual(sample, repository._data)

        get.assert_called_once_with(resource='repos', id=42)

    def test_not_found(self):
        with self.patch_get_error(status_code=404) as get:
            with self.assertRaises(exceptions.DoesNotExist):
                models.Repository.get(id=666)

        self.assertEqual(1, get.call_count)
