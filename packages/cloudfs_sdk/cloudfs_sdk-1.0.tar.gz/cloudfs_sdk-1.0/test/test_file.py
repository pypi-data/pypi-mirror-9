from test_settings import SessionTestCase
from cloudfs.private.cloudfs_paths import ExistValues

import unittest
import os
import shutil
import datetime
import requests

from cloudfs.errors import MethodNotImplemented

# Functional tests based around file creation & modification
class FileFunctionalTests(SessionTestCase):

    FORBIDDEN_SETTERS = ['id', 'type', 'is_mirrored']

    def setUp(self):
        super(FileFunctionalTests, self).setUp()

        self.fs = self.s.filesystem()
        self.root = self.fs.root()
        self.test_folder = self.root.create_folder('test', exists=ExistValues.overwrite)
        self.new_file_name = 'test_file.py'
        self.new_file_path = './{}'.format(self.new_file_name)
        self.new_file = self.test_folder.upload(self.new_file_path, exists=ExistValues.overwrite)

        self.download_directory = './download_tests'
        if os.path.exists(self.download_directory):
            shutil.rmtree(self.download_directory)
        os.makedirs(self.download_directory)

    def get_example_object(self):
        return self.new_file

    def test_create_file_from_file(self):
        file_pointer = open(self.new_file_path, 'r')
        file_info = os.stat(self.new_file_path)
        new_file = self.new_file
        self.assertEqual(file_pointer.read(), new_file.read(), "File did not upload correctly!")
        self.assertEqual(new_file.name, self.new_file_name, "New file not named as expected!")
        self.assertEqual(file_info.st_size, new_file.size, "New file size incorrect!")
        self.assertEqual('py', new_file.extension, "File has wrong extension")
        self.assertEqual('file', new_file.type, "")
        self.assertEqual(False, new_file.is_mirrored)
        self.assertEqual(datetime.date.fromtimestamp(new_file.date_created), datetime.date.today(), "Creation date wrong!")

    def test_download_file(self):
        file = self.get_example_object()
        file_pointer = open(self.new_file_path, 'r')
        expected_contents = file_pointer.read()
        file_pointer.close()

        test_cases = [
            #path, name, expected path,
            (self.download_directory, None, os.path.join(self.download_directory, file.name)),
            (os.path.join(self.download_directory, file.name), None, os.path.join(self.download_directory, file.name)),
            (self.download_directory, "test", os.path.join(self.download_directory, "test"))
        ]
        for path, custom_name, expected_path in test_cases:
            file.download(path, custom_name=custom_name)
            self.assertTrue(os.path.exists(expected_path), "File does not exist in the expected location!")
            downloaded_file = open(expected_path)
            downloaded_file_content = downloaded_file.read()
            self.assertEqual(downloaded_file_content, expected_contents, "Downloaded file did not match file on disk!")
            temporary_link = file.download_link()
            response = requests.get(temporary_link)
            self.assertEqual(response.content, expected_contents, "File downloaded through temporary link did not match file on disk!")

            os.remove(expected_path)



    def test_create_file_from_string(self):
        new_file_name = 'test_name'
        new_file_expected_contents = "test content!"
        new_file = self.test_folder.upload("", name=new_file_name, mime='test/mime', file_content=new_file_expected_contents)
        self.assertEqual(new_file.name, new_file_name, "New item had wrong name!")
        folder_contents = self.test_folder.list()
        self.assertEqual(len(folder_contents), 2, "Folder has wrong number of items!")
        found = False
        for item in folder_contents:
            if item.id == new_file.id:
                found = True
                self.assertEqual(item.name, new_file.name, "Got different items from creating item and listing folder!")

        self.assertTrue(found, "Did not find the file we just created!")
        new_file_contents = new_file.read()
        self.assertEqual(new_file_contents, new_file_expected_contents, "File did not contain expected contents!")

    def test_alter_meta(self):
        new_file = self.new_file
        new_name = 'new name.jpeg'
        expected_extension = 'jpeg'
        expected_mime = 'image/jpeg'

        self.assertNotEqual(new_file.name, new_name, "Name should not be set yet!")
        self.assertNotEqual(new_file.extension, expected_extension, "extension should not be set yet!")

        new_file.name = new_name

        now = self.current_time()
        self.assertEqual(new_file.name, new_name, "Name should be set!")
        # times not being updated :(
        #self.assertTrue(datetime.datetime.fromtimestamp(new_file.date_meta_last_modified) >= now, "Date meta last modified not updated! {} < {}".format(datetime.datetime.fromtimestamp(new_file.date_meta_last_modified), now))

        new_file = self.test_folder.list()[0]

        self.assertEqual(new_file.name, new_name, "Name should be set!")
        self.assertEqual(new_file.mime, expected_mime, "Mime should be set!")
        self.assertEqual(new_file.extension, expected_extension, "Extension should be set!")

        # Can only change the mime if we aren't also changing the name.
        # Otherwise mime will be set from the name of the file.
        new_mime = 'blah/blah'
        new_file.mime = new_mime

        self.assertEqual(new_file.mime, new_mime, "Mime should be set!")
        new_file = self.test_folder.list()[0]

        self.assertEqual(new_file.mime, new_mime, "Mime should be set!")

    def test_file_refresh(self):
        new_name = 'new name.jpeg'
        old_name = self.new_file.name
        # hackz
        self.new_file.data['name'] = new_name
        self.assertEqual(self.new_file.name, new_name, "Name should be set!")
        self.new_file.refresh()
        self.assertEqual(self.new_file.name, old_name, "Name should be reset!")

    def test_file_interface(self):
        file_text = '0123456789'
        new_file = self.test_folder.upload("", name='blah', file_content=file_text)
        s = new_file.read(1)
        self.assertEqual(s, file_text[0])
        s = new_file.read(3)
        self.assertEqual(s, file_text[1:4])
        s = new_file.read(10)
        self.assertEqual(s, file_text[4:])
        new_file.seek(0, 0)
        s = new_file.read(1)
        self.assertEqual(s, file_text[0])
        new_file.seek(1, 1)
        s = new_file.read(1)
        self.assertEqual(s, file_text[2])

    def test_move_copy_files(self):
        second_folder = self.root.create_folder("test2")
        self.assertEqual(len(second_folder.list()), 0)
        self.new_file.move(second_folder)
        self.assertEqual(len(second_folder.list()), 1)
        self.assertEqual(second_folder.list()[0], self.new_file)
        self.assertEqual(str(self.new_file.path), '{}/{}'.format(second_folder.path , self.new_file.id))

        self.assertEqual(len(self.test_folder.list()), 0)
        copy = self.new_file.copy(self.test_folder)
        self.assertEqual(len(self.test_folder.list()), 1)
        self.assertEqual(self.test_folder.list()[0].name, second_folder.list()[0].name)
        self.assertNotEqual(self.test_folder.list()[0], second_folder.list()[0])
        self.assertEqual(second_folder.list()[0].read(), copy.read())

    def test_file_versions(self):
        new_name_one = "another name"
        new_name_two = "another another name"
        self.new_file.name = new_name_one
        self.new_file.name = new_name_two
        previous_versions = self.new_file.versions()
        self.assertEqual(len(previous_versions), 2)
        self.assertEqual(previous_versions[0].name, self.new_file_name)
        self.assertEqual(previous_versions[1].name, new_name_one)

        promoted_file = previous_versions[0].promote()

        self.assertEqual(promoted_file.name, self.new_file_name)
        previous_versions = promoted_file.versions()
        self.assertEqual(len(previous_versions), 3)
        self.assertEqual(previous_versions[2].name, new_name_two)


    def test_unimplemented_methods(self):
        zero_arg_methods = [
            self.new_file.readline,
            self.new_file.readlines,
            self.new_file.truncate,
        ]

        one_arg_methods = [
            self.new_file.write,
            self.new_file.writelines
        ]

        for method in zero_arg_methods:
            self.assertRaises(
                MethodNotImplemented,
                method
            )

        for method in one_arg_methods:
            self.assertRaises(
                MethodNotImplemented,
                method,
                None
            )

    # bug inspired test cases

    def test_upload_to_root(self):
        self.root.upload(self.new_file_path, exists=ExistValues.overwrite)


    def tearDown(self):
        if os.path.exists(self.download_directory):
            shutil.rmtree(self.download_directory)
        for folder in self.root.list():
            folder.delete(force=True, commit=True)



if __name__ == '__main__':
    unittest.main()