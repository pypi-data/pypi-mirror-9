import StringIO
from os.path import exists, isdir, split, join

from private.filesystem_common import create_items_from_json, ItemState
from private.cloudfs_paths import VersionConflictValue, ExistValues
from private.utils import set_debug

from item import Item
from errors import method_not_implemented, operation_not_allowed, invalid_argument


class File(Item):
    """
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/file-operations/
    """
    def __init__(self, rest_interface, data, parent_path=None, parent_state=None):
        super(File, self).__init__(rest_interface, data, parent_path, parent_state)
        self.offset = 0

    def _refresh_request(self, debug=False):
        set_debug(self, debug)
        return self.rest_interface.file_get_meta(self.path)

    @staticmethod
    def _get_download_callback(fp, close=True):
        # preserve env
        def callback(response):
            for chunk in response.iter_content(chunk_size=128):
                if chunk:
                    fp.write(chunk)
                    fp.flush()
            fp.seek(0)
            if close:
                fp.close()

        return callback

    def move(self, dest, exists=ExistValues.rename, debug=False):
        """Move file to destination.

        :param dest:        Path or Folder to move the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if hasattr(dest, 'path'):
            dest = dest.path
        self._state.check_operation_allowed("move")
        result = self.rest_interface.move_file(self.path, dest, self.name, exists)
        self._state.move(dest)

        return result

    def copy(self, dest, exists=ExistValues.rename, debug=False):
        """Copy file to destination.

        :param dest:        Path or Folder to copy the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if hasattr(dest, 'path'):
            dest = dest.path
        self._state.check_operation_allowed("copy")
        result = self.rest_interface.copy_file(self.path, dest, self.name, exists)
        file_copy = create_items_from_json(self.rest_interface, result['meta'], dest, self._state)
        return file_copy[0]


    def delete(self, commit=False, debug=False, force=False):
        """Delete the file.

        :param commit:  If true, will permanently remove the file. Will move to trash otherwise. Defaults to False.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:   Success and the deleted files last version.
        :rtype:     Dictionary.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("delete")
        if self.in_trash:
            if commit:
                set_debug(self, debug)
                result = self.rest_interface.delete_trash_item(self.path)
                self._state.delete(commit, force, result)
                return result
            else:
                # nop
                # we're already in the trash, does not make sense to make a delete call if commit is not true.
                return {}

        set_debug(self, debug)
        result = self.rest_interface.delete_file(self.path, commit)
        self._state.delete(commit, force, result)
        return result

    def promote(self, debug=False):
        """Promote this version of the file and replace the current version.

        This function will throw an exception if called on a file that is not a previous version.
        Updates this file object to the promoted & current file.

        :return:                        Updated file.
        :rtype:                         File object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("promote")
        set_debug(self, debug)

        version = self._get('version', None)

        response = self.rest_interface.promote_file_version(self.path, version)
        self._initialize_self(response)
        self._state.promote(response)
        return self

    def change_attributes(self, values, if_conflict=VersionConflictValue.fail, debug=False):
        """Make bulk changes to this file

        See notes on individual setters for quirks.

        :param values:              Dictionary of attribute:value pairs to change the file.
        :param if_conflict:         Behavior if the local folder information is out of date.
        :param debug:               If true, will print the the request and response to stdout.

        :returns:                   Updated File.
        :rtype:                     File
        :raises SessionNotLinked:   CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError: Based on CloudFS Error Code.
        """
        #TODO: Figure out interface for returning keys
        self._state.check_operation_allowed("change_attributes")
        for key, value in values.iteritems():
            self._set(key, value, save=False)

        return self._save(if_conflict=if_conflict, debug=debug)

    def _save(self, if_conflict=VersionConflictValue.fail, debug=False):
        self._state.check_operation_allowed("change_attributes")
        set_debug(self, debug)
        changes = {'version':self.data['version']}
        for changed_key in self.changed_meta:
            changes[changed_key] = self.data[changed_key]

        self.changed_meta.clear()
        response =  self.rest_interface.file_alter_meta(self.path, changes, if_conflict)
        self._initialize_self(response)
        return self

    def versions(self, start_version=0, end_version=None, limit=10, debug=False):
        """List the previous versions of this file

        The list of files returned are mostly non-functional, though their meta-data is correct. They cannot be read /
        moved / copied, etc.

        :param start_version:   Lowest version number to list. Optional, defaults to listing all file versions.
        :param end_version:     Last version of the file to list. Optional, defaults to listing the most recent version of the file.
        :param limit:           Limit on number of versions returned. Optional, defaults to 10.
        :return:                Previous versions of this file.
        :rtype:                 List of File.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """

        self._state.check_operation_allowed("versions")
        set_debug(self, debug)
        results = self.rest_interface.list_file_versions(self.path, start_version, end_version, limit)
        if len(results) > 0:
            results = create_items_from_json(self.rest_interface, results, self.path[:-1], ItemState.OldVersionState())
        return results

    def download(self, local_path, custom_name=None, debug=False):
        """Download the file to the local filesystem.

        Does not replicate any metadata.
        If downloads are started with synchronous=True CloudFS SDK will attempt to block until all downloads are complete on destruction. This may block your
        program from exiting. To avoid this, call wait_for_downloads at least once with any arguments (i.e. call with a timeout of 0 to halt downloads immediately)


        :param local_path:  Path on local filesystem. Can end with a file name, which will be created or overwritten. Will not create any folders.
        :param custom_name: Can use a separate argument to specify local file name. If file name is included in both local_path and this, local_path takes priority. Optional.
        :param debug:       If true, will print the the request and response to stdout.
        :return:            None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        :raises InvalidArgument:        Based on CloudFS Error Code.
        """
        #TODO: Look into downloading from shares
        self._state.check_operation_allowed("download")
        set_debug(self, debug)

        file_name = custom_name
        local_path_except = invalid_argument('local_path', 'Full path of a folder or file that exists. Alternatively, a non-existent file in an existing hierarchy of folders', local_path)

        if exists(local_path):
            if isdir(local_path):
                # use our name / custom name in directory
                folder_path = local_path
            else:
                # use whole users' path
                folder_path, file_name = split(local_path)
                if not file_name:
                    raise local_path_except
        else:
            folders, file = split(local_path)
            if exists(folders):
                file_name = file
                folder_path = folders
            else:
                raise local_path_except

        if not file_name:
            file_name = self.name


        full_path = join(folder_path, file_name)
        fp = open(full_path, 'wb')

        self.rest_interface.download(self.path, self._get_download_callback(fp, True))

    def download_link(self):
        """Returns a direct link to the file that can be accessed from any device.

        :Warning: This link is temporary, but cannot be revoked in any way before the timer expires (within 24 hours).

        :return: Direct to content accessible without authentication.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        :raises InvalidArgument:        Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("download_link")
        return self.rest_interface.download(self.path, None, return_direct_link=True)

    # file interface
    def read(self, size=None, debug=False):
        """File-like interface to read file. Reads size bytes from last offset.

        Reads file synchronously - does not start threads.
        Warning: Each read() call generates on request to CloudFS.


        :param size:    Number of bytes to read. If None, will read entire file. Defaults to None.
        :param debug:   If true, will print the the request and response to stdout.
        :return:        File contents.
        :rtype:         String
        """
        self._state.check_operation_allowed("read")
        set_debug(self, debug)
        range = None
        fp = StringIO.StringIO()
        if size:
            range = [self.tell(), self.tell() + size - 1]
            self.offset += size
        if self.in_share:
            fp.write(self.rest_interface.download_share(self._state.share_key, self.path))
            fp.seek(0)
        else:
            self.rest_interface.download(self.path, self._get_download_callback(fp, False), range=range)

        return fp.read()

    def readline(self, size=None):
        """ Read until reaching a line break bytes read reaches :size:.

        :note: Not implemented.

        :param size:    Max number of bytes to read before returning. Optional, no size limit if not specified.
        :return:    Data from file.
        :rtype:     String
        """
        raise method_not_implemented(self, 'readline')

    def readlines(self, sizehint=None):
        """ Reads entire file into list.

        Each list entry is either a line (ending in a '\\n' character) or is close to :sizehint: bytes.

        :note: Not implemented.

        :param sizehint:    Approximate limit on list entry size. Optional, no size limit if not specified.
        :return:    Data from file.
        :rtype:     String
        """
        raise method_not_implemented(self, 'readlines')

    def seek(self, offset, whence=0):
        """Seek to the given offset in the file.

        :param offset:  Number of bytes to seek.
        :param whence:  Seek be
        :return:        resulting offset
        :rtype:         int
        """
        self._state.check_operation_allowed("seek")
        if whence == 0:
            self.offset = offset
        if whence == 1:
            self.offset += offset
        if whence == 2:
            self.offset = self.data['length'] - offset

        if offset > self.size:
            offset = self.size
        if offset < 0:
            offset = 0

        return offset

    def tell(self):
        """
        :return: Current offset of file-like interface.
        :rtype:  int
        """
        return self.offset

    def truncate(self, size=0):
        """Delete all data in file after :size: byte.

        :note: Not implemented.

        :param size:    Number of bytes of current file to keep. Optional, defaults to 0.
        :return:        None
        """
        raise method_not_implemented(self, 'truncate')


    def write(self, data):
        """Append data to file.

        :note: Not implemented.

        :param data:    Data to append to the file.
        :return:        None
        """
        raise method_not_implemented(self, 'write')

    def writelines(self, lines):
        """Write the objects contained in lines to the file.

        :note: Not implemented.

        :param lines:   Iterable container of data to add to the file.
        :return:        None
        """
        raise method_not_implemented(self, 'writelines')

    @property
    def extension(self):
        """
        :setter: Disabled
        :return: Extension of file.
        :rtype:  String
        """
        return self._get('extension')

    @extension.setter
    def extension(self, new_extension):
        raise operation_not_allowed("Setting extension directly instead of name")

    @property
    def mime(self):
        """
        :setter: Enabled
        :return: Mime type of file.
        :rtype:  String
        """
        return self._get('mime')

    @mime.setter
    def mime(self, new_mime):
        self._set('mime', new_mime)

    @property
    def size(self):
        """
        :setter: Disabled
        :return: Size of file.
        :rtype:  int
        """
        return self._get('size')

    @size.setter
    def size(self, new_size):
         raise operation_not_allowed("Setting the size of an Item")

    def __str__(self):
        return "{}({})[File|{}]:{} {} bytes".format(self.name.encode('utf-8'), self.mime.encode('utf-8'), str(self._state), self.id, self.size)
