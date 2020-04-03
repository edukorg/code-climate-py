from datetime import datetime

from requests import HTTPError

from code_climate import exceptions
from code_climate.client import CodeClimateClient


def _as_date(date_str):
    if not date_str:
        return None
    return datetime.fromisoformat(date_str.replace('Z', "+00:00"))


class EmbeddedModel:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise exceptions.UnexpectedDataFormat()

        self._data = data

    def __getitem__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise exceptions.UnexpectedDataFormat()


class BaseModel(EmbeddedModel):
    _RESOURCE_NAME = None

    @property
    def id(self):
        try:
            return self._data['id']
        except KeyError:
            raise exceptions.UnexpectedDataFormat()

    def __getitem__(self, item):
        try:
            return self._data['attributes'][item]
        except KeyError:
            raise exceptions.UnexpectedDataFormat()

    @classmethod
    def get(cls, id):
        try:
            data = CodeClimateClient.get(resource=cls._RESOURCE_NAME, id=id)
        except HTTPError as e:
            if e.response.status_code == 404:
                raise exceptions.DoesNotExist()
            raise

        item = data['data']
        return cls(data=item)

    @classmethod
    def list(cls, params=None):
        for item in CodeClimateClient.paginate(resource=cls._RESOURCE_NAME, params=params):
            yield cls(data=item)

    def _related(self, resource_class):
        items = CodeClimateClient.paginate(
            resource=resource_class._RESOURCE_NAME,
            id=self.id,
            from_resource=self._RESOURCE_NAME,
        )
        for item in items:
            yield resource_class(data=item)


class UnsupportedModelMixin:
    @classmethod
    def get(cls, id):
        raise exceptions.UnsupportedModelException()

    @classmethod
    def list(cls, params=None):
        raise exceptions.UnsupportedModelException()

    def _detail(self, resource_class):
        raise exceptions.UnsupportedModelException()


class TestReport(UnsupportedModelMixin, BaseModel):
    _RESOURCE_NAME = 'test_reports.json'

    @property
    def branch(self):
        return self['branch']

    @property
    def commit_sha(self):
        return self['commit_sha']

    @property
    def committed_at(self):
        return _as_date(self['committed_at'])

    @property
    def covered_percent(self):
        return self['covered_percent'] / 100

    @property
    def rating(self):
        return Rating(data=self['rating'])

    @property
    def received_at(self):
        return _as_date(self['received_at'])

    @property
    def state(self):
        return self['state']


class Rating(EmbeddedModel):
    @property
    def path(self):
        return self['path']

    @property
    def letter(self):
        return self['letter']

    @property
    def pillar(self):
        return self['pillar']

    @property
    def measure(self):
        return self['measure']['value'] / 100
