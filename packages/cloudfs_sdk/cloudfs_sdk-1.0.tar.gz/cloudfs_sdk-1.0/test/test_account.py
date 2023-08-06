import unittest

from test_settings import CloudFSTestCase
from cloudfs.session import Session
from cloudfs import errors

class AccountTest(CloudFSTestCase):

    FORBIDDEN_SETTERS = ['id', 'storage_usage', 'state_display_name', 'state_id',
                           'plan_id', 'over_storage_limit', 'storage_usage',
                           'storage_limit', 'plan_display_name']

    def setUp(self):
        self.s = Session(self.CLOUDFS_BASE,
                self.CLOUDFS_ID,
                self.CLOUDFS_SECRET)

        self.assertRaises(
            errors.CloudFSError,
            self.s.account
        )

        self.s.authenticate(self.TEST_USER_EMAIL, self.TEST_USER_PASSWORD)
        self.assertEqual(True, self.s.is_linked(), "Authentication failed.")

    def get_example_object(self):
        return self.s.account()

    def test_account(self):
        acct = self.get_example_object()
        # basic field check
        self.assertTrue(acct.storage_usage >= 0, 'Usage expected to be above 0!')
        self.assertTrue(acct.storage_limit >= 0)
        self.assertEqual(acct.plan_display_name, u'CloudFS End User', 'Account should be CloudFS End User Apparently!')
        self.assertTrue(acct.id is not '', 'Empty account id.')
        self.assertEqual(acct.storage_usage > acct.storage_limit, acct.over_storage_limit, 'Over storage limit flag does not reflect storage numbers!')
        self.assertEqual(acct.state_display_name, 'Active', 'Account is active!')
        self.assertTrue(acct.session_locale != '', 'Session locale not set!')
        self.assertTrue(acct.locale != '', 'Account locale not set!')

if __name__ == '__main__':
    unittest.main()