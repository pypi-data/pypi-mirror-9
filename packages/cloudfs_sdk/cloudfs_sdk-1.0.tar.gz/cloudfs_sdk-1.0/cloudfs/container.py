import os

from private.utils import set_debug
from private.filesystem_common import create_items_from_json
from private.cloudfs_paths import VersionConflictValue, ExistValues

from item import Item

class Container(Item):
    """
    The Container class exists as a basis for Share and Folder items.

    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/folder-operations/
    """
    def list(self, debug=False):
        """List the contents of this container.

        :param debug:       If true, will print the the request and response to stdout.
        :return:            Contents of the container.
        :rtype:             Array of Items
        """
        self._state.check_operation_allowed("list")
        set_debug(self, debug)

        if self.in_share:
            response = self.rest_interface.browse_share(self._state.share_key, self.path)
        elif self.in_trash:
            response = self.rest_interface.list_trash(self.path)
        else:
            response = self.rest_interface.list_folder(self.path)

        path = self.path if str(self.path) != '/' else None

        return create_items_from_json(self.rest_interface, response, path, self._state)


class Folder(Container):
    """
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/folder-operations/
    """
    @staticmethod
    def root_folder(rest_interface):
        data = {
            'name':'ROOT',
            'id':'',
            'type':'folder',
            'is_mirrored': False,
            'date_content_last_modified':0,
            'date_created':0,
            'date_meta_last_modified':0,
            'application_data':{}
            }
        return Folder(rest_interface, data)

    def _refresh_request(self, debug=False):
        if debug:
            self.rest_interface.debug_requests(1)
        return self.rest_interface.folder_get_meta(self.path)

    def upload(self, filesystem_path, name=None, mime=None, exists=ExistValues.fail, file_content=None, debug=False):
        """Upload a file to CloudFS.

        :Note: File content can be read from a file or passed into the file_content parameter.

        :param filesystem_path: Source of file data.
        :param name:            Name of file in CloudFS. If left blank, will use name of file in path.
        :param mime:            Mine for new file. If left blank, mime will be detected.
        :param exists:          Behavior if the given name exists on CloudFS. Defaults to fail.
        :param data_inline:     Flag to indicate if the source is a string or a filename.
        :param debug:           If true, will print the the request and response to stdout.

        :returns:               Uploaded file.
        :rtype:                 File object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("upload")
        set_debug(self, debug)
        if not name:
            name = os.path.basename(filesystem_path)

        if not file_content:
            # pass in a handle
            file_content = open(filesystem_path, 'rb')

        files = {'file':[name, file_content]}

        if mime:
            files['file'].append(mime)

        upload_response = self.rest_interface.upload(self.path, files, exists)
        return create_items_from_json(self.rest_interface, upload_response, self.path, self._state)[0]

    def create_folder(self, container_or_name, exists=ExistValues.fail, debug=False):
        """Create a new folder in this folder.

        :param container_or_name:   Container or String name. If arg is a Container, will use that Containers name.
        :param debug:               If true, will print the the request and response to stdout.

        :returns:       New folder.
        :rtype:         Folder object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("create_folder")
        set_debug(self, debug)

        if isinstance(container_or_name, Item):
            container_or_name = container_or_name.name

        new_folder_response = self.rest_interface.create_folder(self.path, container_or_name, exists)
        return create_items_from_json(self.rest_interface, new_folder_response, self.path)[0]

    def copy(self, dest, exists=ExistValues.rename, debug=False):
        """Copy folder to destination.

        :param dest:        Path or Folder to copy the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        # TODO: update "new" item
        if hasattr(dest, 'path'):
            dest = dest.path
        self._state.check_operation_allowed("copy")
        result = self.rest_interface.copy_folder(self.path, dest, self.name, exists)
        file_copy = create_items_from_json(self.rest_interface, result['meta'], dest, self._state)
        return file_copy

    def move(self, dest, exists=ExistValues.rename, debug=False):
        """Move file to destination.

        :param dest:        Path or Folder to move the items to.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.

        :returns:   None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        # TODO: update internal data
        if hasattr(dest, 'path'):
            dest = dest.path
        self._state.check_operation_allowed("move")
        result = self.rest_interface.move_folder(self.path, dest, self.name, exists)
        self._state.move(dest)

        return result

    def change_attributes(self, values, if_conflict=VersionConflictValue.fail, debug=False):
        """Make bulk changes to this folder

        See notes on individual setters for quirks.

        :param if_conflict:         Behavior if the local folder information is out of date.
        :param debug:               If true, will print the the request and response to stdout.

        :returns:                   Updated folder.
        :rtype:                     Folder object
        :raises SessionNotLinked:   CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError: Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("change_attributes")
        for key, value in values.iteritems():
            self._set(key, value, save=False)

        return self._save(if_conflict=if_conflict, debug=debug)

    def _save(self, if_conflict=VersionConflictValue.fail, debug=False):
        set_debug(self, debug)
        changes = {'version':self.data['version']}
        for changed_key in self.changed_meta:
            changes[changed_key] = self.data[changed_key]

        self.changed_meta.clear()

        response = self.rest_interface.folder_alter_meta(self.path, changes, if_conflict)
        self._initialize_self(response)
        return self

    def delete(self, commit=False, force=False, debug=False):
        """Delete folder.

        Folder will only be removed from trash if commit is True. This is the case for folders in or out of the trash, so folders
        that are in the trash already will treat delete(commit=False) calls as a no-op.


        :param commit:  If true, will permanently remove file instead of moving it to trash. Defaults to False.
        :param force:   If true, will delete folder even if it contains items. Defaults to False.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:   Success and the deleted folders last version.
        :rtype:     Dictionary
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        self._state.check_operation_allowed("delete")
        set_debug(self, debug)
        if self.in_trash:
            if commit:
                result = self.rest_interface.delete_trash_item(self.path)
                self._state.delete(commit, force, result)
                return result
            else:
                # nop
                # we're already in the trash, does not make sense to make a delete call if commit is not true.
                return {}
        else:
            result =  self.rest_interface.delete_folder(self.path, commit, force)
            self._state.delete(commit, force, result)
            return result

    def __str__(self):
        return "{}[Folder|{}]:{}".format(self.name.encode('utf-8'), self._state, self.id)