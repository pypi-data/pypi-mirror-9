
from private.utils import set_debug
from private.cloudfs_paths import VersionConflictValue, ExistValues, RestoreValue
from private.cached_object import CachedObject
from private.filesystem_common import ItemState

from errors import operation_not_allowed
from path import Path

import json


class Item(CachedObject):
    """
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/file-operations/
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/folder-operations/
    """

    def __init__(self, rest_interface, data, parent_path=None, parent_state=None):
        super(Item, self).__init__(rest_interface, data)
        self._create_from_json(data, parent_path)
        self._state = ItemState(self, parent_state)

    def _create_from_json(self, data, parent_path=None):
        if not parent_path:
            self._full_path = Path.path_from_string('/')
        elif isinstance(parent_path, Item):
            self._full_path = parent_path.path.copy()
        elif isinstance(parent_path, str):
            self._full_path = Path.path_from_string(parent_path)
        else:
            self._full_path = parent_path.copy()

        self._full_path.append(self.id)

    def _initialize_self(self, request_info, x_headers={}):
        if 'meta' in request_info:
            request_info = request_info['meta']
        self.data = request_info

    @property
    def in_share(self):
        return self._state.share_key != None

    @property
    def in_trash(self):
        return self._state.in_trash

    @property
    def old_version(self):
        return self._state.old_version

    # setters and getters
    @property
    def name(self):
        """

        :note: if name is set on a File, both extension and mime will be updated based on the new name of the File.

        :setter: Enabled
        :return: Name of item in filesystem.
        :rtype: String
        """
        return self._get('name')

    @name.setter
    def name(self, new_name):
        self._set('name', new_name)

    @property
    def id(self):
        """
        :setter: Disabled
        :return: Id of item in filesystem. Used for paths.
        :rtype: String
        """
        return self._get('id')

    @id.setter
    def id(self, new_id):
        raise operation_not_allowed("Setting the id of an Item")

    @property
    def path(self):
        """
        :setter: Disabled
        :return: Full path to item.
        :rtype: String
        """
        return self._full_path

    @path.setter
    def path(self, new_path):
        raise operation_not_allowed("Setting the path of an Item directly")

    @property
    def type(self):
        """
        :setter: Disabled
        :return: Type string of item in filesystem. Roughly corresponds to object type.
        :rtype: String
        """
        return self._get('type')

    @type.setter
    def type(self, new_type):
        raise operation_not_allowed("Setting the type of an Item")

    @property
    def is_mirrored(self):
        """

        :note: Not currently used in CloudFS.

        :setter: Disabled
        :return: If this item is currently being synced with a file on the users' desktop.
        :rtype: Bool
        """
        return self._get('is_mirrored')

    @is_mirrored.setter
    def is_mirrored(self, new_mirrored_flag):
        raise operation_not_allowed("Setting if an Item is mirrored")

    @property
    def date_content_last_modified(self):
        """
        :setter: Disabled
        :return: Timestamp for the last time the content of this item was modified. In seconds.
        :rtype: int
        """
        return self._get('date_content_last_modified', 0)

    @date_content_last_modified.setter
    def date_content_last_modified(self, new_date_content_last_modified):
        raise operation_not_allowed("Setting the last modified time.")

    @property
    def date_created(self):
        """
        :setter: Enabled
        :return: Timestamp this item was created. In seconds.
        :rtype: int
        """
        return self._get('date_created', 0)

    @date_created.setter
    def date_created(self, new_date_created):
        raise operation_not_allowed("Setting the creation time.")

    @property
    def date_meta_last_modified(self):
        """
        :setter: Disabled
        :return: Timestamp for the last time the metadata was modified for this item. In Seconds.
        :rtype: int
        """
        return self._get('date_meta_last_modified', 0)

    @date_meta_last_modified.setter
    def date_meta_last_modified(self, new_date_meta_last_modified):
        raise operation_not_allowed("Setting the meta last modified time.")

    @property
    def application_data(self):
        """
        :setter: Enabled. Takes a dictionary or a JSON string.
        :return: Misc data storage. Contents are not defined in any way.
        :rtype: Dictionary
        """
        return self._get('application_data', {})

    @application_data.setter
    def application_data(self, new_application_data):
        if type(new_application_data) is not str:
            new_application_data = json.dumps(new_application_data)
        self._set('application_data', new_application_data)
        # TODO: Add application data test

    def move(self, dest, exists=ExistValues.rename, debug=False):
        raise Exception('Move not implemented for item base class!')

    def copy(self, dest, exists=ExistValues.rename, debug=False):
        raise Exception('Copy not implemented for item base class!')


    def delete(self, commit=False, force=False, debug=False):
        """ Not implemented in this class, but implemented on sub-classes.
        """
        raise Exception('Delete not implemented for item base class!')

    def _save(self, if_conflict=VersionConflictValue.fail, debug=False):
        raise Exception('_save not implemented for item base class!')

    def change_attributes(self, values, if_conflict=VersionConflictValue.fail, debug=False):
        """ Not implemented in this class, but implemented on sub-classes.
        """
        raise Exception('Save not implemented for item base class!')

    def restore(self, restore_method=RestoreValue.fail, method_argument=None, maintain_validity=False, debug=False):
        """Restore item from trash.


        :return:    True if successful, exception otherwise.
        :rtype:     List of Items
        """
        # TODO: update data after restore
        self._state.check_operation_allowed('restore')
        if not self.in_trash:
            return self

        set_debug(self, debug)
        self.rest_interface.restore_trash_item(self.path, restore_method, method_argument)
        self._state.restore(restore_method, method_argument, maintain_validity)
        return self

    def __eq__(self, other):
        if hasattr(other, 'data') and 'id' in getattr(other, 'data'):

            return self.data['id'] == getattr(other, 'data')['id']
        return False

    def __str__(self):
        return 'Item:{}'.format(self.id)

    def __repr__(self):
        return self.__str__()