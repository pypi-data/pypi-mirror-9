from private.filesystem_common import create_items_from_json
from private.cached_object import CachedObject
from private.cloudfs_paths import ExistValues
from private.utils import set_debug

from path import Path
from errors import operation_not_allowed, method_not_implemented, SharePasswordError
from item import Item, ItemState

class Share(CachedObject):
    @staticmethod
    def _share_from_share_key(rest_interface, share_key, password=None, debug=None):
        """ Fetch the share associated with a share key.

        This is the intended method for retrieving a share from another user.

        :param rest_interface:      Rest interface that will retrieve the share. Should be associated with the account of the user who will receive the share.
        :param share_key:           Key identifying the share.
        :param password:            Password for share if necessary. Optional.
        :param debug:               If true, will print the the request and response to stdout.
        :return:                    The share associated with the share key.
        :rtype:                     Share Object
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises SharePasswordError:     If the share requires a password and one is not provided.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        data = {'share_key':share_key}
        share = Share(rest_interface, data)
        if password:
            share._unlock(password, debug)

        try:
            share.refresh(debug)
        except SharePasswordError, e:
            raise SharePasswordError(e.request, e.response, e.message)

        return share

    def _refresh_request(self, debug=False):
        set_debug(self, debug)
        return self.rest_interface.browse_share(self.share_key)['share']

    @property
    def path(self):
        """
        :setter: Disabled
        :return: A Path containing the share key.
        :rtype: String
        """
        return Path.path_from_string_list([self.data['share_key']])

    @path.setter
    def path(self, new_path):
        raise operation_not_allowed("Setting the path of an Item directly")

    @property
    def share_key(self):
        """
        :setter: Disabled
        :return: Key for this share.
        :rtype: String
        """
        return self._get('share_key')

    @property
    def name(self):
        """
        :setter: Enabled
        :return: Name for the share.
        :rtype: String
        """
        return self._get('share_name')

    @name.setter
    def name(self, new_name):
        self._set('share_name', new_name)

    @property
    def size(self):
        """
        :setter: Disabled
        :return: Size of the share.
        :rtype: int
        """
        return self._get("share_size", 0)

    @size.setter
    def size(self, new_size):
         raise operation_not_allowed("Setting the size of an Item")

    @property
    def date_content_last_modified(self):
        """
        :setter: Disabled
        :return: Timestamp for the last time the content of this share was modified. In seconds.
        :rtype: int
        """
        return self._get('date_content_last_modified', 0)

    @date_content_last_modified.setter
    def date_content_last_modified(self, new_date_content_last_modified):
        raise operation_not_allowed("Setting the last modified time.")

    @property
    def date_meta_last_modified(self):
        """
        :setter: Enabled
        :return: Timestamp for the last time the metadata was modified for this share. In Seconds.
        :rtype: int
        """
        return self._get('date_meta_last_modified', 0)

    @date_meta_last_modified.setter
    def date_meta_last_modified(self, new_date_meta_last_modified):
        raise operation_not_allowed("Setting the meta last modified time.")

    @property
    def application_data(self):
        """
        :setter: Disabled
        :return: Misc data storage. Contents are not defined in any way.
        :rtype: Dictionary
        """
        return self._get('application_data', {})

    @application_data.setter
    def application_data(self, new_application_data):
        raise method_not_implemented(self, 'set application_data')

    def list(self, debug=False):
        """List the contents of the share
        :param debug:   If true, will print the the request and response to stdout.
        :return:        Items in share.
        :rtype:         List of items.
        """
        set_debug(self, debug)
        results = self.rest_interface.browse_share(self.share_key)
        return create_items_from_json(self.rest_interface, results, None, ItemState.ShareState(self.share_key))

    def receive(self, path=None, exists=ExistValues.rename, debug=False):
        """Add share contents to the filesystem of this user.

        Behaves differently depending on how the share was crated.
        See Filesystem::create_share for notes on behavior of this command.

        :param location:    Location to copy the share to. Optional, defaults to root.
        :param exists:      How to handle if an item of the same name exists in the destination folder. Defaults to rename.
        :param debug:       If true, will print the the request and response to stdout.
        :return:            Items created by receiving this share on the users' filesystem.
        :rtype:             List of Items.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        set_debug(self, debug)
        if isinstance(path, Item):
            path = path.path

        result = self.rest_interface.receive_share(self.share_key, path, exists)
        return create_items_from_json(self.rest_interface, result, path)


    def change_attributes(self, values, password=None, debug=False):
        """Make bulk changes to this share

        Shares only support changing the name of the share, but this interface is included
        for consistency with Item.

        :param if_conflict:         Behavior if the local folder information is out of date.
        :param debug:               If true, will print the the request and response to stdout.

        :returns:                   Updated share.
        :rtype:                     Share
        :raises SessionNotLinked:   CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError: Based on CloudFS Error Code.
        """
        for key, value in values.iteritems():
            if key == 'name' or key == 'share_name':
                self._set('share_name', value, save=False)
        return self._save(password=password, debug=debug)

    def _save(self, password=None, debug=False):
        set_debug(self, debug)
        if 'share_name' in self.changed_meta:
            # don't do anything if we don't have a new name - nothing else to change
            response = self.rest_interface.alter_share_info(self.share_key, password, new_name=self.name)
            self._initialize_self(response)

        self.changed_meta.clear()
        return self

    def set_password(self, password, old_password=None, debug=False):
        """Change password for the share.

        :param password:        New password for share.
        :param old_password:    Current password for share. Optional, but required if a password exists.
        :param debug:           If true, will print the the request and response to stdout.
        :return:                The modified share.
        :rtype:                 Share object.
        :raises SharePasswordError:     If the share requires a password and one is not provided.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        set_debug(self, debug)
        response = self.rest_interface.alter_share_info(self.share_key, old_password, password)
        self._initialize_self(response)
        return self

    def _unlock(self, password, debug=False):
        set_debug(self, debug)
        self.rest_interface.unlock_share(self.share_key, password)
        return self

    def delete(self, debug=False):
        """Delete the share.

        There is no trash for shares. Use with caution.

        :param debug:   If true, will print the the request and response to stdout.
        :return:        None
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        if debug:
            self.rest_interface.debug_requests(1)
        self.rest_interface.delete_share(self.path)

    def __str__(self):
        return '{}[Shr] {}bytes'.format(self.name, self.size)