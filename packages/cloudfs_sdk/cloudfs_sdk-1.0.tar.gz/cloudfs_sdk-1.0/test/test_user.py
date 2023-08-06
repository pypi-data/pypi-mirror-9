import unittest
import datetime

from test_settings import CloudFSTestCase
from cloudfs.session import Session
from cloudfs import errors

class UserTests(CloudFSTestCase):

    FORBIDDEN_SETTERS = ['id', 'username', 'last_login', 'created_at']
    UNIMPLEMENTED_SETTERS = ['email', 'first_name', 'last_name']

    def setUp(self):
        self.s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertRaises(
            errors.CloudFSError,
            self.s.user
        )

        self.s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, self.s.is_linked(), "Authentication failed.")

    def tearDown(self):
        self.s.unlink()

    def get_example_object(self):
        return self.s.user()

    # def test_create_user(self):
    #     self.s.set_admin_credentials(self.ADMIN_ID, self.ADMIN_SECRET)
    #     self.s.create_account('test6', '111111')

    def test_user(self):
        # intended to test basic funnctionality
        user = self.get_example_object()
        self.assertEqual('', user.email, 'Email is not blank!')
        self.assertEqual(self.TEST_USER_EMAIL, user.username, 'Username is not the one set in the admin panel')
        # last_login is in ms
        self.assertEqual(datetime.date.today(), datetime.date.fromtimestamp(user.last_login/1000), 'Last login is not today!')
        self.assertTrue(user.id != '', 'Missing user id!')
        self.assertTrue(user.created_at != '', 'Missing user creation time!')

    def test_user_stub(self):
        self.assertRaises(
            errors.MethodNotImplemented,
            self.get_example_object().save
        )

if __name__ == '__main__':
    unittest.main()