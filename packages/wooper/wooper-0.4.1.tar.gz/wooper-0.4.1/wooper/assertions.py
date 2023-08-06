"""
declassified methods from unittest.TestCase
"""


from unittest import TestCase

from .general import WooperAssertionError


assertions = TestCase()
assertions.failureException = WooperAssertionError
assertions._diffThreshold = 2**16
assertions._maxDiff = None
assertions.DIFF_OMITTED = ('\nDiff is %s characters long. '
                           'Set self.maxDiff to None to see it.')
assertions._MAX_LENGTH = 80
assertions._PLACEHOLDER_LEN = 12
assertions._MIN_BEGIN_LEN = 5
assertions._MIN_END_LEN = 5
assertions._MIN_COMMON_LEN = 5


# def assert_is_instance(obj, cls, msg=None):
#     """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
#     default message."""
#     return assertions.assertIsInstance(obj, cls, msg)


def assert_equal(first, second, msg=None):
    """Fail if the two objects are unequal as determined by the '=='
       operator.
    """
    return assertions.assertEqual(first, second, msg=None)


def assert_not_equal(first, second, msg=None):
    """Fail if the two objects are equal as determined by the '!='
       operator.
    """
    return assertions.assertNotEqual(first, second, msg=None)


def assert_in(member, container, msg=None):
    """Just like self.assertTrue(a in b), but with a nicer default message."""
    return assertions.assertIn(member, container, msg)


def assert_not_in(member, container, msg=None):
    """Just like self.assertTrue(a not in b), but with a nicer default message.
    """
    return assertions.assertNotIn(member, container, msg)
