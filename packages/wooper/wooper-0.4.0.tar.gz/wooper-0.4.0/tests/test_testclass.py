from unittest import TestCase
from requests.structures import CaseInsensitiveDict
from wooper.test_class import ApiMixin
from wooper.general import WooperAssertionError
from .common import response


class ExpectStatusTestCase(TestCase, ApiMixin):

    server_url = 'http://google.com'

    def test_pass(self):
        self.GET('/')
