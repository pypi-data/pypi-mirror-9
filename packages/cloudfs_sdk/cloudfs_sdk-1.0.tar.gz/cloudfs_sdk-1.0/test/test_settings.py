if __package__ is None:
    import os
    from os import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import datetime
from cloudfs.session import Session
from cloudfs.errors import OperationNotAllowed, MethodNotImplemented


class CloudFSTestCase(unittest.TestCase):
    # fill in with the details from your cloudfs account
    # Application Client ID
    CLOUDFS_ID = ''
    # Application Secret
    CLOUDFS_SECRET = ''
    # Application API Server
    CLOUDFS_BASE = ''

    # Admin Id and Secret are issued to CloudFS accounts above the "free" tier and allow the creation of
    # user accounts programmatically. If you want to run these tests simply fill in your credentials.
    ADMIN_ID = ''
    ADMIN_SECRET = ''

    # user settings
    TEST_USER_EMAIL = ''
    TEST_USER_PASSWORD = ''
    SECOND_TEST_USER_EMAIL = ''
    SECOND_TEST_USER_PASSWORD = ''

    # not needed for setting up your account

    UNIMPLEMENTED_SETTERS = []
    FORBIDDEN_SETTERS = []

    def get_example_object(self):
        return None

    def test_unimplemented_setters(self):
        def set_attr_helper(property):
            example = self.get_example_object()
            if example:
                setattr(example, property, None)
            else:
                # fake error if child test isn't setup
                raise OperationNotAllowed("")

        for method in self.UNIMPLEMENTED_SETTERS:
            try:
                self.assertRaises(
                    MethodNotImplemented,
                    set_attr_helper,
                    method
                )
            except:
                example = self.get_example_object()
                raise AssertionError("Method {}.{} did not raise expected {}.".format(type(example), method, OperationNotAllowed))

    def test_forbidden_setters(self):
        def set_attr_helper(property):
            example = self.get_example_object()
            if example:
                setattr(example, property, None)
            else:
                # fake error if child test isn't setup
                raise OperationNotAllowed("")

        for method in self.FORBIDDEN_SETTERS:
            try:
                self.assertRaises(
                    OperationNotAllowed,
                    set_attr_helper,
                    method
                )
            except:
                example = self.get_example_object()
                raise AssertionError("Method {}.{} did not raise expected {}.".format(type(example), method, OperationNotAllowed))

    def current_time(self):
        now = datetime.datetime.now()
        return now - datetime.timedelta(microseconds=now.microsecond)

class SessionTestCase(CloudFSTestCase):
    def setUp(self):
        self.s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, self.s.is_linked(), "Authentication failed.")