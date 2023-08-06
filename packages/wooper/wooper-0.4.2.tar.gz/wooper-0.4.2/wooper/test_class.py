"""
.. module:: test_class
   :synopsis: Testclass and mixing for using together with unittest

.. moduleauthor:: Yauhen Kirylau <actionless.loveless@gmail.com>

"""

import json
from requests import Session
from pprint import pprint
from unittest import TestCase

from .expect import (
    expect_status, expect_status_in,
    expect_json, expect_json_match, expect_json_contains,
    expect_headers, expect_headers_contain,
    expect_json_length, expect_body_contains,
)


class ApiMixin:
    """
    This class can be used as a mixin to `unittest.TestCase
    <https://docs.python.org/3.4/library/unittest.html#unittest.TestCase>`_
    to provide additional methods for requesting, inspecting and testing
    REST API services.
    """

    server_url = None
    """ Server URL """

    maxDiff = None
    print_url = False
    print_payload = False
    print_headers = False

    session = None

    response = None

    def _apply_path(self, json_dict, path):
        if not path:
            return json_dict
        path_elements = path.split('/')
        for element in path_elements:
            if element.startswith('['):
                try:
                    element = int(element.lstrip('[').rstrip(']'))
                except ValueError as e:
                    self.fail("Path can't be applied: {exception}."
                              .format(exception=e.args))
            try:
                json_dict = json_dict[element]
            except (IndexError, TypeError, KeyError):
                self.fail(
                    """Path can't be applied:
no such index '{index}' in \"\"\"{dict}\"\"\"."""
                    .format(index=element, dict=json_dict))
        return json_dict

    def get_url(self, uri):
        return self.server_url + uri

    def request(self, method, uri, *args,
                headers=None, add_server=True, **kwargs):
        if not self.session:
            self.session = Session()

        if add_server:
            url = self.get_url(uri)
        else:
            url = uri

        if self.print_url:
            print('{method} {url}'.format(method=method, url=url))
        if self.print_payload and 'data' in kwargs:
            pprint(kwargs['data'])
        if self.print_headers:
            pprint(headers)

        self.response = self.session.request(
            method, url, *args,
            verify=False, headers=headers, **kwargs)

    def request_with_data(self, method,  uri, data='', *args, **kwargs):
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        self.request(method, uri, *args, data=data, **kwargs)

    def GET(self, *args, **kwargs):
        self.request('GET', *args, **kwargs)

    def POST(self, *args, **kwargs):
        self.request_with_data('POST', *args, **kwargs)

    def PATCH(self, *args, **kwargs):
        self.request_with_data('PATCH', *args, **kwargs)

    def PUT(self, *args, **kwargs):
        self.request_with_data('PUT', *args, **kwargs)

    def DELETE(self, *args, **kwargs):
        self.request('DELETE', *args, **kwargs)

    @property
    def json_response(self):
        try:
            return json.loads(self.response.text)
        except ValueError:
            self.fail('Response in not a valid JSON.')

    def inspect_json(self, path=None):
        json_response = self._apply_path(self.json_response, path)
        pprint(json_response)

    def inspect_body(self):
        pprint(self.response.text)

    def inspect_status(self):
        print(self.response.status_code)

    def inspect_headers(self):
        pprint(dict(self.response.headers))

    def expect_status(self, code):
        """
        checks if response status equals given code

        :param int code: Expected status code

        """
        expect_status(self.response, code)

    def expect_status_in(self, codes):
        """
        checks if response status equals to one of the provided

        :param list codes: List of valid status codes

        """
        expect_status_in(self.response, codes)

    def expect_json(self, expected_json, path=None):
        """
        checks if json response equals some json,

        :param expected_json: JSON object to compare with
        :type expected_json: str, list, dict

        :param path: Path inside response json,
            separated by slashes, ie 'foo/bar/spam', 'foo/[0]/bar'
        :type path: str, optional

        """
        expect_json(self.response, expect_json, path)

    def expect_json_match(self, expected_json, path=None):
        """
        checks if json response partly matches some json,

        :param expected_json: JSON object to compare with
        :type expected_json: str, list, dict

        :param path: Path inside response json,
            separated by slashes, ie 'foo/bar/spam', 'foo/[0]/bar'
        :type path: str, optional

        """
        expect_json_match(self.response, expected_json, path)

    def expect_json_contains(self, expected_json, path=None,
                             reverse_expectation=False):
        """
        checks if json response contains some json subset,

        :param expected_json: JSON object to compare with
        :type expected_json: str, list, dict

        :param path: Path inside response json,
            separated by slashes, ie 'foo/bar/spam', 'foo/[0]/bar'
        :type path: str, optional

        """
        expect_json_contains(self.response, expected_json, path,
                             reverse_expectation)

    def expect_json_not_contains(self, expected_json, path=None):
        """
        checks if json response not contains some json subset,

        :param expected_json: JSON object to compare with
        :type expected_json: str, list, dict

        :param path: Path inside response json,
            separated by slashes, ie 'foo/bar/spam', 'foo/[0]/bar'
        :type path: str, optional

        """
        expect_json_contains(self.response, expected_json, path,
                             reverse_expectation=True)

    def expect_headers(self, headers, partly=False):
        """
        checks if response headers values are equal to given

        :param dict headers: Dict with headers and their values,
            like { "Header1": "ExpectedValue1" }

        :param partly: Compare full header value or
            check if the value includes expected one.
        :type partly: bool, optional

        """
        expect_headers(self.response, headers, partly)

    def expect_headers_contain(self, header, value=None):
        """
        checks if response headers contain a given header

        :param str header: Expected header name.

        :param value: Expected header value.
        :type value: str, optional

        """
        expect_headers_contain(self.response, header, value)

    def expect_json_length(self, length, path=None):
        """
        checks if count of objects in json response equals provided length,

        :param int length: Expected number of objects inside json
            or length of the string

        :param path: Path inside response json,
            separated by slashes, ie 'foo/bar/spam', 'foo/[0]/bar'
        :type path: str, optional

        """
        expect_json_length(self.response, length)

    def expect_body_contains(self, text):
        """
        checks if response body contains some text

        :param str text: Expected text
        """
        expect_body_contains(self.response, text)


class ApiTestCase(TestCase, ApiMixin):
    pass
