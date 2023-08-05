
from unittest import TestCase
from qubell.api.testing import BaseComponentTestCase

import os


class TestMeta(TestCase):
    def restore(self, params):
        return params

    def setUp(self):
        self.cls = BaseComponentTestCase
        self.cls.organization = self
        self.cls.organization.restore = self.restore

    def test_meta_url(self):
        meta = self.cls.upload_metadata_applications("https://raw.githubusercontent.com/qubell-bazaar/component-mysql-dev/1.1-35p/meta.yml")
        assert 'Database' in meta['applications'][0]['name']

    def test_meta_file(self):
        meta = self.cls.upload_metadata_applications(os.path.join(os.path.dirname(__file__), "./meta.yml"))
        assert 'Database' in meta['applications'][0]['name']
