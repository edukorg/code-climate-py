import os

import requests

from code_climate import exceptions


class CodeClimateClient:
    _URL = 'https://api.codeclimate.com/v1'
    _TOKEN = os.environ.get('CODECLIMATE_API_TOKEN')

    @classmethod
    def _get_headers(cls):
        if not cls._TOKEN:
            raise exceptions.TokenUndefinedException()

        return {
            "Accept": "application/vnd.api+json",
            "Authorization": f"Token token={cls._TOKEN}",
        }

    @classmethod
    def get(cls, resource, id=None, from_resource=None, params=None):
        if from_resource:
            if not id:
                raise UnboundLocalError()
            url = f'{cls._URL}/{from_resource}/{id}/{resource}'
        elif id:
            url = f'{cls._URL}/{resource}/{id}'
        else:
            url = f'{cls._URL}/{resource}'

        response = requests.get(
            url=url,
            params=params,
            headers=cls._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def paginate(cls, resource, page_size=100, params=None, id=None, from_resource=None):
        params = params or {}

        page = 1
        while True:
            params = params.copy()
            params['page[number]'] = page
            params['page[size]'] = page_size

            data = cls.get(resource=resource, id=id, from_resource=from_resource, params=params)
            items = data['data']
            if not items:
                break

            for item in data['data']:
                yield item

            page += 1
