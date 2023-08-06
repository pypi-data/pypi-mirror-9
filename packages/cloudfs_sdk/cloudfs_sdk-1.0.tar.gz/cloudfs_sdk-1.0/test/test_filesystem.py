from test_settings import SessionTestCase
import unittest
from cloudfs.private.cloudfs_paths import ExistValues

class FilesystemTests(SessionTestCase):
    def setUp(self):
        super(FilesystemTests, self).setUp()

        self.fs = self.s.filesystem()
        self.root = self.fs.root()
        self.file_content = "check out this file"
        self.test_folder = self.root.create_folder('test', exists=ExistValues.overwrite)
        self.test_file = self.test_folder.upload("", 'test_name', file_content=self.file_content)

    def test_list_root(self):
        test_folder2 = self.test_folder.create_folder('test')
        test_folder2_2 = self.fs.get_item(test_folder2.path)

        self.assertTrue(test_folder2.id == test_folder2_2.id)

    def test_get_item(self):
        folder = self.fs.get_item(self.test_folder.path)
        folder.list()
        self.assertEqual(folder.type, 'folder')
        file = self.fs.get_item(self.test_file.path)
        self.assertEqual(file.read(), self.file_content)
        self.assertEqual(file.type, 'file')

    def tearDown(self):
        for folder in self.root.list():
            folder.delete(force=True, commit=True)
        for item in self.fs.list_trash():
            item.delete(commit=True)

if __name__ == '__main__':
    unittest.main()