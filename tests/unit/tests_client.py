import json
import unittest
from unittest.mock import patch

import httpretty

from code_climate import client, exceptions


class HTTPPrettyTestMixin:
    @property
    def request_count(self):
        return len(httpretty.httpretty.latest_requests)

    @property
    def latest_request_header(self):
        last_request = httpretty.httpretty.last_request
        return last_request.headers


class TestCodeClimateClient(HTTPPrettyTestMixin, unittest.TestCase):
    API_URL = 'https://api.codeclimate.com/v1'

    def patch_token(self, token='42'):
        return patch('code_climate.client.CodeClimateClient._TOKEN', token)

    def test_token_not_set(self):
        with self.assertRaises(exceptions.TokenUndefinedException):
            client.CodeClimateClient.get(
                resource='potato',
            )

    @httpretty.activate
    def test_request_error(self):
        httpretty.register_uri(
            httpretty.GET,
            f'{self.API_URL}/potato',
            body="Find the best daily deals",
            status=404,
        )

        with self.patch_token():
            with self.assertRaises(Exception):
                client.CodeClimateClient.get(
                    resource='potato',
                )

        self.assertEqual(1, self.request_count)
        self.assertEqual('Token token=42', self.latest_request_header['Authorization'])

    @httpretty.activate
    def test_list_resource(self):
        httpretty.register_uri(
            httpretty.GET,
            f'{self.API_URL}/potato',
            body=json.dumps([{'answer': 314}]),
        )

        with self.patch_token():
            data = client.CodeClimateClient.get(
                resource='potato',
            )

        self.assertEqual(1, self.request_count)
        self.assertEqual('Token token=42', self.latest_request_header['Authorization'])
        self.assertEqual([{'answer': 314}], data)

    @httpretty.activate
    def test_detail_resource(self):
        httpretty.register_uri(
            httpretty.GET,
            f'{self.API_URL}/potato/314',
            body=json.dumps({'answer': 314}),
        )

        with self.patch_token():
            data = client.CodeClimateClient.get(
                resource='potato',
                id=314,
            )

        self.assertEqual(1, self.request_count)
        self.assertEqual('Token token=42', self.latest_request_header['Authorization'])
        self.assertEqual({'answer': 314}, data)

    @httpretty.activate
    def test_detail_from_resource(self):
        httpretty.register_uri(
            httpretty.GET,
            f'{self.API_URL}/potato/314/answers',
            body=json.dumps([{'answer': 314}]),
        )

        with self.patch_token():
            data = client.CodeClimateClient.get(
                from_resource='potato',
                id=314,
                resource='answers',
            )

        self.assertEqual(1, self.request_count)
        self.assertEqual('Token token=42', self.latest_request_header['Authorization'])
        self.assertEqual([{'answer': 314}], data)

    @httpretty.activate
    def test_detail_from_resource_without_id(self):
        with self.patch_token():
            with self.assertRaises(UnboundLocalError):
                client.CodeClimateClient.get(
                    from_resource='potato',
                    resource='answers',
                )

        self.assertEqual(0, self.request_count)
