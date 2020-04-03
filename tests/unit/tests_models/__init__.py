from unittest.mock import patch

from requests import HTTPError, Response

from tests import SampleTestMixin
from tests.unit.tests_client import HTTPPrettyTestMixin


class ModelTestMixin(SampleTestMixin, HTTPPrettyTestMixin):
    API_URL = 'https://api.codeclimate.com/v1'

    @property
    def sample_name(self):
        raise NotImplementedError()

    def patch_get(self, data, per_page=1):
        many = isinstance(data, (list, tuple))
        if many:
            def chunks(lst, n):
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]

            responses = [
                {'data': items}
                for items in chunks(lst=data, n=per_page)
            ]
            responses.append({'data': []})
            kwargs = {
                'side_effect': responses
            }
        else:
            kwargs = {
                'return_value': {'data': data}
            }
        return patch('code_climate.client.CodeClimateClient.get', **kwargs)

    def patch_get_error(self, content=None, status_code=404):
        response = Response()
        response.status_code = status_code
        response._content = content
        error = HTTPError(response=response)
        return patch('code_climate.client.CodeClimateClient.get', side_effect=error)

    def assertPaginated(self, patched, resource, number_of_pages, from_resource=None, id=None):
        self.assertEqual(number_of_pages, patched.call_count)

        for i in range(number_of_pages):
            call_args = {
                'resource': resource,
                'from_resource': from_resource,
                'id': id,
                'params': {
                    'page[number]': i+1,
                    'page[size]': 100,
                },
            }
            patched.assert_any_call(**call_args)

    def test_fields(self):
        raise NotImplementedError()

    def test_invalid_field(self):
        raise NotImplementedError()

    def test_list(self):
        raise NotImplementedError()

    def test_detail(self):
        raise NotImplementedError()

    def test_not_found(self):
        raise NotImplementedError()
