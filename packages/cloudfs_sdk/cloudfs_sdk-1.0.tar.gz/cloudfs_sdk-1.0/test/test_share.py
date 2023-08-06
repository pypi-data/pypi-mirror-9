from test_settings import SessionTestCase
from cloudfs import ExistValues, SharePasswordError, OperationNotAllowed, WrongStateForOperation
import unittest


class ShareFunctionalTests(SessionTestCase):
    def setUp(self):
        super(ShareFunctionalTests, self).setUp()

        self.fs = self.s.filesystem()
        self.root = self.fs.root()
        self.file_content = "check out this file"
        self.test_folder = self.root.create_folder('test', exists=ExistValues.overwrite)
        self.inner_folder = self.test_folder.create_folder('share_folder', exists=ExistValues.overwrite)
        self.test_file = self.inner_folder.upload("", 'test_name', file_content=self.file_content)
    def get_example_object(self):
        return None

    def test_share(self):
        self.assertEqual(len(self.fs.list_shares()), 0, 'Should not have any shares!')
        share = self.fs.create_share(self.test_folder)
        self.assertEqual(len(self.fs.list_shares()), 1, 'Should have one share!')
        share.delete()
        self.assertEqual(len(self.fs.list_shares()), 0, 'Should not have any shares!')

    def test_share_download(self):
        share = self.fs.create_share(self.test_folder)
        folder = share.list()[0]
        file = folder.list()[0]
        self.assertEqual(file.read(), self.file_content)

    def test_list_share(self):
        share = self.fs.create_share(self.test_folder)
        contents = share.list()
        self.assertEqual(len(contents), 1, 'Share did not contain anything')
        self.assertEqual(contents[0].type, 'folder', 'Share did not contain a folder')
        self.assertEqual(contents[0].name, self.inner_folder.name, 'Folder had wrong name')
        self.assertEqual(contents[0].id, self.inner_folder.id, 'Folder had wrong name')
        share_folder = contents[0]
        share_folder_contents = share_folder.list()
        self.assertEqual(len(share_folder_contents), 1, 'Share folder did not contain anything')
        self.assertEqual(share_folder_contents[0].type, 'file', 'Share folder did not contain a file')
        self.assertEqual(share_folder_contents[0].name, self.test_file.name, 'File had wrong name')
        self.assertEqual(share_folder_contents[0].id, self.test_file.id, 'File had wrong name')
        share_file = share_folder_contents[0]
        changed_name = "another name for some reason"

        # ensure we disable the appropriate methods on files and folders from shares
        disabled_methods_common = [
            ['change_attributes', [{'name':changed_name}]],
            ['delete', []],
            ['move', ['']],
            ['copy', ['']],
            ['restore', []]
        ]

        for method_info in disabled_methods_common:
            method = getattr(share_file, method_info[0])
            # TODO: find a less ugly way to do this
            if len(method_info[1]):
                self.assertRaises(
                    WrongStateForOperation,
                    method,
                    *method_info[1]
                )
            else:
                self.assertRaises(
                    WrongStateForOperation,
                    method
                )

            method = getattr(share_folder, method_info[0])
            if len(method_info[1]):
                self.assertRaises(
                    WrongStateForOperation,
                    method,
                    *method_info[1]
                )
            else:
                self.assertRaises(
                    WrongStateForOperation,
                    method
                )


    def test_receive_share(self):
        folder = self.root.create_folder("share receive folder")
        share = self.fs.create_share(self.inner_folder)
        share.receive()
        root_contents = self.root.list()
        self.assertEqual(len(root_contents), 3, "Share item not created in root!")
        shared_folder = None
        for item in root_contents:
            if item.type == 'folder' and item.name == self.inner_folder.name:
                shared_folder = item

        self.assertTrue(shared_folder != None, "Could not find shared folder!")
        self.assertNotEqual(shared_folder.id, self.inner_folder.id, "folder has same id!")
        shared_folder_contents = shared_folder.list()
        self.assertEqual(len(shared_folder_contents), 1, "Shared folder has wrong name!")
        self.assertEqual(shared_folder_contents[0].name, self.test_file.name, "file did not have expected name!")
        self.assertNotEqual(shared_folder_contents[0].id, self.test_file.id, "file has same id!")
        self.assertEqual(shared_folder_contents[0].read(), self.test_file.read(), "file did not have same contents!")

        share.receive(folder)
        folder_contents = folder.list()
        self.assertEqual(len(folder_contents), 1, "Share item not created in new folder!")
        self.assertEqual(folder_contents[0].name, self.inner_folder.name, "file did not have expected name!")
        self.assertNotEqual(folder_contents[0].id, self.inner_folder.id, "file has same id!")
        shared_folder_contents = folder_contents[0].list()
        self.assertEqual(len(shared_folder_contents), 1, "Shared folder has wrong name!")
        self.assertEqual(shared_folder_contents[0].name, self.test_file.name, "file did not have expected name!")
        self.assertNotEqual(shared_folder_contents[0].id, self.test_file.id, "file has same id!")
        self.assertEqual(shared_folder_contents[0].read(), self.test_file.read(), "file did not have same contents!")

    def test_alter_share(self):
        new_name = "test name"
        share = self.fs.create_share(self.test_folder)
        shares = self.fs.list_shares()
        self.assertEqual(shares[0].name, share.name, "Share name not the same!")
        share.name = new_name
        self.assertEqual(share.name, new_name, "Name change not reflected locally!")
        new_shares = self.fs.list_shares()
        self.assertEqual(share.name, new_shares[0].name, "Name change not reflected on server!")
        self.assertNotEqual(shares[0].name, new_shares[0].name, "Old copy has somehow updated its name?!")
        shares[0].refresh()
        self.assertEqual(shares[0].name, new_shares[0].name, "Name change found by refresh!")

    def test_share_password(self):
        test_password = "test password"
        share = self.fs.create_share(self.inner_folder)
        share.set_password(test_password)
        share_key = share.share_key
        self.s.authenticate(self.SECOND_TEST_USER_EMAIL, self.SECOND_TEST_USER_PASSWORD)
        fs = self.s.filesystem()
        root = fs.root()

        self.assertRaises(
            SharePasswordError,
            fs.retrieve_share,
            share_key
        )
        share = fs.retrieve_share(share_key, test_password)

        share.receive(root)
        contents = root.list()
        self.assertEqual(len(contents), 1, "Extra items in test user 2's filesystem")
        self.assertEqual(contents[0].name, self.inner_folder.name, "Share folder was not received properly.")
        contents_contents = contents[0].list()
        self.assertEqual(len(contents_contents), 1, "Extra items in test user 2's filesystem")
        self.assertEqual(contents_contents[0].name, self.test_file.name, "Share file was not received properly.")
        self.assertEqual(contents_contents[0].read(), self.test_file.read(), "Share file was not received properly.")

    def test_share_change_password(self):
        test_password = "test password"
        test_password2 = "test password 2"
        share = self.fs.create_share(self.test_folder)
        self.s.authenticate(self.SECOND_TEST_USER_EMAIL, self.SECOND_TEST_USER_PASSWORD)
        fs = self.s.filesystem()
        share.set_password(test_password, debug=True)
        # Currently bugged
        # self.assertRaises(
        #     SharePasswordError,
        #     share.set_password,
        #     test_password2
        # )

        share2 = fs.retrieve_share(share.share_key, test_password)
        self.assertEqual(share.share_key, share2.share_key, "Share keys do not match!")
        self.assertRaises(
            SharePasswordError,
            fs.retrieve_share,
            share.share_key, test_password2,
        )

        share.set_password(test_password2, test_password)
        share2 = fs.retrieve_share(share.share_key, test_password2)
        self.assertRaises(
            SharePasswordError,
            fs.retrieve_share,
            share.share_key, test_password,
        )

        share.set_password(test_password, test_password2)
        fs.retrieve_share(share.share_key, test_password)
        self.assertRaises(
            SharePasswordError,
            fs.retrieve_share,
            share.share_key, test_password2,
        )

    def test_create_multi_path_share(self):
        folder = self.root.create_folder("another share folder")
        expected_folders = [folder, self.inner_folder]
        share = self.fs.create_share(expected_folders)
        found = 0
        for item in share.list():
            if item.name in [f.name for f in expected_folders]:
                found += 1

        self.assertEqual(found, len(expected_folders))

    def tearDown(self):
        for folder in self.root.list():
            folder.delete(force=True, commit=True)
        for share in self.fs.list_shares():
            share.delete()

        self.s.authenticate(self.SECOND_TEST_USER_EMAIL, self.SECOND_TEST_USER_PASSWORD)
        fs = self.s.filesystem()
        for folder in fs.root().list():
            folder.delete(force=True, commit=True)
        for share in fs.list_shares():
            share.delete()



if __name__ == '__main__':
    unittest.main()