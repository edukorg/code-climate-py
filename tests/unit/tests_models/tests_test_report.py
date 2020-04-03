import unittest
from datetime import datetime, timezone

from code_climate import models, exceptions
from tests.unit.tests_models import ModelTestMixin


class TestModelTestReport(ModelTestMixin, unittest.TestCase):
    @property
    def sample_name(self):
        return 'test_reports'

    def test_fields(self):
        data = self.samples[0]
        report = models.TestReport(data=data)

        self.assertEqual('5e822176f155b24d66663b05', report.id)
        self.assertEqual('rs-not-potato', report.branch)
        self.assertEqual('a3b3d16a166498f1bd3667092d1a9085bb9a11cb', report.commit_sha)
        self.assertEqual(0.9599720670391061, report.covered_percent)
        self.assertEqual('done', report.state)

        committed_at = datetime(2020, 3, 30, 16, 35, 38, 0, tzinfo=timezone.utc)
        self.assertEqual(committed_at, report.committed_at)

        received_at = datetime(2020, 3, 30, 16, 42, 30, 115000, tzinfo=timezone.utc)
        self.assertEqual(received_at, report.received_at)

        self.assertEqual('/', report.rating.path)
        self.assertEqual('D', report.rating.letter)
        self.assertEqual(0.9599720670391061, report.rating.measure)

    def test_invalid_field(self):
        report = models.TestReport(data={})
        with self.assertRaises(exceptions.UnexpectedDataFormat):
            report.commit_sha  # pylint: disable=pointless-statement

    def test_list(self):
        data = self.samples
        with self.patch_get(data=data) as get:
            with self.assertRaises(exceptions.UnsupportedModelException):
                models.TestReport.list()

        get.assert_not_called()

    def test_detail(self):
        data = self.samples[0]
        with self.patch_get(data=data) as get:
            with self.assertRaises(exceptions.UnsupportedModelException):
                models.TestReport.get(id=42)
        get.assert_not_called()

    def test_not_found(self):
        with self.patch_get(data=[]) as get:
            with self.assertRaises(exceptions.UnsupportedModelException):
                models.TestReport.get(id=42)
        get.assert_not_called()
