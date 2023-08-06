from unittest import TestCase
from requests.structures import CaseInsensitiveDict
from wooper import expect
from wooper.general import WooperAssertionError
from .common import response


class ExpectStatusTestCase(TestCase):

    def test_pass(self):
        response.status_code = 200
        expect.expect_status(response, 200)

    def test_fail(self):
        response.status_code = 403
        with self.assertRaises(WooperAssertionError):
            expect.expect_status(response, 200)


class ExpectStatusInTestCase(TestCase):

    def test_pass(self):
        response.status_code = 200
        expect.expect_status_in(response, {200, 201})

    def test_fail(self):
        response.status_code = 400
        with self.assertRaises(WooperAssertionError):
            expect.expect_status_in(response, {200, 401, 500})


class ExpectJsonTestCase(TestCase):

    def setUp(self):
        response.text = """{
            "foo": "bar",
            "list": [ {"baz": "spam"}, "1", "qwe" ]
        }"""

    def test_pass(self):
        expect.expect_json(
            response,
            """{
                "foo": "bar",
                "list": [ {"baz": "spam"}, "1", "qwe" ]
            }"""
        )

    def test_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json(
                response,
                """{
                    "foo": "bar",
                    "list": [ {"baz": "spa"}, "1", "qwe" ]
                }"""
            )

    def test_path_pass(self):
        expect.expect_json(
            response,
            "spam",
            path="list/[0]/baz"
        )

    def test_path_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json(
                response,
                "spa",
                path="list/[0]/baz"
            )


class ExpectJsonMatchTestCase(TestCase):

    def setUp(self):
        response.text = """
        {
            "query1": {
                "and": [{
                    "test1": "value1"
                }, {
                    "test3": "value3"
                }],
                "test2": "value2",
                "test4": "value4"
            },
            "query10": "value10",
            "test5": "value5"
        }
        """
        self.list_response_text = """
        [
            {"query1": {
                "and": [{
                    "test1": "value1"
                }, {
                    "test3": "value3"
                }],
                "test2": "value2",
                "test4": "value4"
            }},
            {"query10": "value10"},
            {"test5": "value5"}
        ]
        """

    def test_pass(self):
        expect.expect_json_match(
            response,
            {
                "query1": {
                    "and": [{
                        "test1": "value1"
                    }],
                    "test2": "value2"
                },
                "query10": "value10"
            }
        )

    def test_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_match(
                response,
                {
                    "query1": {
                        "and": [{
                            "test1": "wrongvalue1"
                        }],
                        "test2": "value2"
                    },
                    "query10": "value10"
                }
            )

    def test_list_pass(self):
        response.text = self.list_response_text
        expect.expect_json_match(
            response,
            [
                {"query1": {
                    "and": [{
                        "test1": "value1"
                    }],
                    "test2": "value2"
                }},
                {"query10": "value10"}
            ]
        )

    def test_list_fail(self):
        response.text = self.list_response_text
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_match(
                response,
                [
                    {"query1": {
                        "and": [{
                            "test1": "wrongvalue1"
                        }],
                        "test2": "value2"
                    }},
                    {"query10": "value10"}
                ]
            )


class ExpectJsonContainsTestCase(TestCase):

    def setUp(self):
        response.text = """{
            "foo": "bar",
            "list": [
                {
                    "baz": "spam",
                    "second": "item"
                },
                1,
                "qwe",
                ["a", "b"]
            ]
        }"""

    def test_fulljson_pass(self):
        expect.expect_json_contains(
            response,
            """{
                "foo": "bar",
                "list": [
                    {"baz": "spam", "second": "item"},
                    1,
                    "qwe",
                    ["a", "b"]
                ]
            }"""
        )

    def test_fulljson_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_contains(
                response,
                """{
                    "foo": "bar",
                    "list": [
                        {"baz": "spam", "other": "item"},
                        1,
                        "qwe",
                        ["a", "b"]
                    ]
                }"""
            )

    def test_object_in_object_pass(self):
        expect.expect_json_contains(
            response,
            {
                "list":
                [{"baz": "spam", "second": "item"}, 1, "qwe", ["a", "b"]]
            }
        )

    def test_object_in_object_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_contains(
                response,
                {
                    "list":
                    [{"baz": "spa", "second": "item"}, 1, "qwe", ["a", "b"]]
                }
            )

    def test_object_in_array_pass(self):
        expect.expect_json_contains(
            response,
            {"baz": "spam", "second": "item"},
            path="list"
        )

    def test_object_in_array_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_contains(
                response,
                {"baz": "spa", "second": "item"},
                path="list"
            )

    def test_array_in_array_pass(self):
        expect.expect_json_contains(
            response,
            ['a', 'b'],
            path="list"
        )

    def test_array_in_array_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_contains(
                response,
                ['a', 'b', 'c'],
                path="list"
            )

    def test_item_in_array_pass(self):
        expect.expect_json_contains(
            response,
            1,
            path="list"
        )

    def test_item_in_array_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_contains(
                response,
                2,
                path="list"
            )

    def test_item_pass(self):
        expect.expect_json_contains(
            response,
            "spam",
            path="list/[0]/baz"
        )

    def test_partitem_pass(self):
        expect.expect_json_contains(
            response,
            "spa",
            path="list/[0]/baz"
        )

    def test_item_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_contains(
                response,
                "span",
                path="list/[0]/baz"
            )


class ExpectJsonNotContainsTestCase(TestCase):

    def setUp(self):
        response.text = """{
            "foo": "bar",
            "list": [
                {
                    "baz": "spam",
                    "second": "item"
                },
                1,
                "qwe",
                ["a", "b"]
            ]
        }"""

    def test_object_in_object_pass(self):
        expect.expect_json_not_contains(
            response,
            {
                "list":
                [{"baz": "spam", "second": "item"}, 1, "qwe", ["a", "c"]]
            }
        )

    def test_object_in_object_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_not_contains(
                response,
                {
                    "list":
                    [{"baz": "spam", "second": "item"}, 1, "qwe", ["a", "b"]]
                }
            )

    def test_object_in_array_pass(self):
        expect.expect_json_not_contains(
            response,
            {"baz": "spa", "second": "item"},
            path="list"
        )

    def test_object_in_array_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_not_contains(
                response,
                {"baz": "spam", "second": "item"},
                path="list"
            )


class ExpectHeadersTestCase(TestCase):

    def setUp(self):
        response.headers = CaseInsensitiveDict({
            "content-type": "application/json",
            "Access-Control-Allow-Origin": "*"
        })

    def test_contains_pass(self):
        expect.expect_headers_contain(
            response,
            "access-control-allow-origin"
        )

    def test_contains_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_headers_contain(
                response,
                "Authorization"
            )

    def test_contains_value_pass(self):
        expect.expect_headers_contain(
            response,
            "access-control-allow-origin", "*"
        )

    def test_contains__value_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_headers_contain(
                response,
                "content-type", "text/html"
            )

    def test_pass(self):
        expect.expect_headers(
            response,
            {"Content-Type": "application/json",
             "access-control-allow-origin": "*"}
        )

    def test_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_headers(
                response,
                {"Content-Type": "text/html",
                 "access-control-allow-origin": "*"}
            )

    def test_partly_pass(self):
        expect.expect_headers(
            response,
            {"Content-Type": "json"},
            partly=True
        )

    def test_partly_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_headers(
                response,
                {"Content-Type": "html"},
                partly=True
            )


class ExpectJsonLenthTestCase(TestCase):

    def setUp(self):
        response.text = """{
            "foo": "bar",
            "list": [ {"baz": "spam"}, "1", "qwe" ]
        }"""

    def test_pass(self):
        expect.expect_json_length(response, 2)

    def test_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json_length(response, 3)

    def test_path_pass(self):
        expect.expect_json(
            response,
            "spam",
            path="list/[0]/baz"
        )

    def test_path_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_json(
                response,
                "spa",
                path="list/[0]/baz"
            )


class ExpectBodyContainsTestCase(TestCase):

    def setUp(self):
        response.text = """404 Not Found"""

    def test_pass(self):
        expect.expect_body_contains(response, "Not Found")

    def test_fail(self):
        with self.assertRaises(WooperAssertionError):
            expect.expect_body_contains(response, "trace")
