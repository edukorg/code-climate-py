import json
import os


class SampleTestMixin:
    @property
    def sample_name(self):
        raise NotImplementedError()

    @property
    def samples(self):
        filename = os.path.join(
            os.path.dirname(__file__),
            'samples',
            f'{self.sample_name}.json'
        )
        with open(filename, 'r') as f:
            return json.loads(f.read())
