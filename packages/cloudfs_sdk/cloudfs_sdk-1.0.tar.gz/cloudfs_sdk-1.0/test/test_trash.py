from test_settings import SessionTestCase
from cloudfs.private.cloudfs_paths import ExistValues, RestoreValue

import unittest

from cloudfs.errors import PathDoesNotExist, NameConflictInOperation, WrongStateForOperation

# Functional tests based around file creation & modification
class TrashFunctionalTests(SessionTestCase):

    def setUp(self):
        super(TrashFunctionalTests, self).setUp()

        self.fs = self.s.filesystem()
        self.root = self.fs.root()
        self.test_folder = self.root.create_folder('test', exists=ExistValues.overwrite)

    def test_trash(self):
        trash_contents = self.fs.list_trash()
        self.assertEqual(len(trash_contents), 0, "Trash was not empty!")
        self.test_folder.delete(commit=False)
        trash_contents = self.fs.list_trash()
        self.assertEqual(len(trash_contents), 1, "Trash had wrong number of items!")

    def test_trash_delete(self):
        trash_contents = self.fs.list_trash()
        self.assertEqual(len(trash_contents), 0, "Trash was not empty!")
        self.test_folder.delete(commit=False)
        trash_contents = self.fs.list_trash()
        self.assertEqual(len(trash_contents), 1, "Trash had wrong number of items!")
        trash_contents[0].delete(commit=False)
        trash_contents = self.fs.list_trash()
        self.assertEqual(len(trash_contents), 1, "Trash item was deleted without commit=True!")
        trash_contents[0].delete(commit=True)
        trash_contents = self.fs.list_trash()
        self.assertEqual(len(trash_contents), 0, "Trash was not empty!")

    def test_trash_restore_fail_option(self):
        new_folder = self.test_folder.create_folder("folder to delete")
        new_folder.delete(commit=False)
        trash_contents = self.fs.list_trash()
        self.assertEqual(new_folder.path, trash_contents[0].path, "path not updated when placing folder in trash")
        new_folder.restore()
        folder_contents = self.root.list()
        self.assertEqual(len(folder_contents), 1, 'Folder was not restored!')
        self.assertEqual(folder_contents[0], self.test_folder, 'Folder was different after being restored!')
        self.assertEqual(len(self.fs.list_trash()), 0, 'Trash was not empty!')
        self.assertEqual(str(new_folder.path), '{}/{}'.format(self.test_folder.path, new_folder.id))

    def test_trash_restore_fail_option_error(self):
        self.test_folder.delete(commit=False)
        self.root.create_folder('test', exists=ExistValues.overwrite)
        trash_contents = self.fs.list_trash()
        self.assertRaises(
            NameConflictInOperation,
            trash_contents[0].restore
        )
        self.assertEqual(len(self.fs.list_trash()), 1, 'Trash was empty!')

    def test_trash_restore_rescue(self):
        self.test_folder.delete(commit=False)
        new_folder = self.root.create_folder('test 2')
        new_folder_contents = new_folder.list()
        self.assertEqual(len(new_folder_contents), 0, 'New folder should not contain anything!')
        self.test_folder.restore(RestoreValue.rescue, new_folder.path)
        new_folder_contents = new_folder.list()
        self.assertEqual(len(new_folder_contents), 1, 'New folder should contain restored folder!')
        self.assertEqual(new_folder_contents[0], self.test_folder, 'Folder contents were not as expected!')
        self.assertEqual(len(self.fs.list_trash()), 0, 'Trash was not empty!')
        self.assertEqual(str(self.test_folder.path), '{}/{}'.format(new_folder.path, self.test_folder.id))

    def test_trash_restore_rescue_fail(self):
        self.test_folder.delete(commit=False)
        new_folder = self.root.create_folder('test 2', exists=ExistValues.overwrite)
        new_folder.create_folder('test')
        self.assertRaises(
            NameConflictInOperation,
            self.test_folder.restore,
            RestoreValue.rescue, new_folder.path
        )
        self.assertEqual(len(self.fs.list_trash()), 1, 'Trash was empty!')

    def test_trash_restore_remake_valid(self):
        self.test_folder.delete(commit=False)
        recreated_name = "recreated folder"
        self.test_folder.restore(RestoreValue.recreate, recreated_name, maintain_validity=True)
        root_contents = self.root.list()
        self.assertEqual(len(root_contents), 1, 'New folder should contain restored folder!')
        self.assertEqual(root_contents[0].name, recreated_name, 'Folder contents were not as expected!')
        self.assertEqual(len(self.fs.list_trash()), 0, 'Trash was not empty!')
        self.assertEqual(str(self.test_folder.path), '{}/{}'.format(root_contents[0].id, self.test_folder.id))

    def test_trash_restore_remake_invalid(self):
        self.test_folder.delete(commit=False)
        recreated_name = "recreated folder"
        self.test_folder.restore(RestoreValue.recreate, recreated_name, maintain_validity=False)
        self.assertRaises(
            WrongStateForOperation,
            self.test_folder.list
            )

    def test_trash_restore_remake_fail(self):
        self.test_folder.delete(commit=False)
        recreated_name = "recreated folder"
        self.root.create_folder(recreated_name)
        self.assertRaises(
            NameConflictInOperation,
            self.test_folder.restore,
            RestoreValue.recreate, recreated_name
        )
        self.assertEqual(len(self.fs.list_trash()), 1, 'Trash was empty!')

    def test_create_in_trash_fail(self):
        self.test_folder.delete(commit=False)
        self.assertRaises(
                WrongStateForOperation,
                self.test_folder.create_folder,
                'should not work'
        )


    def tearDown(self):
        for folder in self.root.list():
            folder.delete(force=True, commit=True)
        for item in self.fs.list_trash():
            item.delete(commit=True)



if __name__ == '__main__':
    unittest.main()