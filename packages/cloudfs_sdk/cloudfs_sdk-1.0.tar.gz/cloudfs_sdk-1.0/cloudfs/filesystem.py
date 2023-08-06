from private.filesystem_common import *
from private.cloudfs_paths import ExistValues
from private.utils import set_debug

from container import Folder
from item import Item, ItemState

class Filesystem(object):

    exists = ExistValues()

    def __init__(self, rest_interface):
            self.rest_interface = rest_interface

    def get_item(self, item, debug=False):
        """Returns an Item object representing a given path.

        This is the only endpoint that supports string paths.

        :Note: This does not support shares, use the retrieve_share function instead.

        :param item:    CFS path as a path or string.
        :param debug:   If true, will print the the request and response to stdout.

        :returns:       Representation the Item at the given path.
        :rtype:         Item object.
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        path = item
        set_debug(self, debug)

        if type(item) is not str:
            path = str(item)

        parent_path = None
        if path.count('/') > 1: # more than root
            parent_path = path.rstrip('/')
            parent_path = parent_path[0:parent_path.rfind('/')]

        meta = self.rest_interface.generic_get_meta(path)
        items = create_items_from_json(self.rest_interface, meta, parent_path, allow_root=True)[0]
        return items

    def root(self):
        """
        :return: The root of the users filesystem.
        :rtype:  Folder object
        """
        return Folder.root_folder(self.rest_interface.get_copy())

    def list_trash(self, debug=False):
        """List the items in the trash.

        :param debug:   If true, will print the the request and response to stdout.
        :return:        Items in trash.
        :rtype:         List of Items.
        """
        set_debug(self, debug)
        result = self.rest_interface.list_trash(self.root().path)
        return create_items_from_json(self.rest_interface, result, None, ItemState.TrashState())

    def list_shares(self, debug=False):
        """Get all share objects this user has created and not deleted.

        :param debug:   If true, will print the the request and response to stdout.
        :return:        Shares made by current user.
        :rtype:         List of Share objects.
        """
        set_debug(self, debug)
        result = self.rest_interface.list_shares()
        return create_items_from_json(self.rest_interface, result, None)

    def retrieve_share(self, share_key, password=None, debug=False):
        """Instantiate a Share object from a string key.

        Will throw an exception if password is needed but not supplied.

        :note: Cannot use shares created in other applications.

        :param share_key:   String reference to a share created by another user.
        :param password:    Password for the share. Optional, but will throw an exception if a password is required and not provided.
        :param debug:       True if successful, exception otherwise.
        :return:            Share specified by the share key.
        :rtype:             Share object.
        """
        from share import Share
        from errors import SharePasswordError
        try:
           return Share._share_from_share_key(self.rest_interface, share_key, password, debug)
        except SharePasswordError, e:
            raise SharePasswordError(e.request, e.response, e.message, e.INTERNAL_CODE)

    def create_share(self, items, password=None, debug=False):
        """Create a new share

        :param items:       Items that should be in the share. These items will be the root of the share unless the list is only one folder. Then the share will contain the folder contents.
        :param password:    Password for share if desired. If omitted, share will be freely accessable with the share key.
        :param debug:       If True, will print the request and response to stdout.
        :return:            Items in share.
        :rtype:             List of Items.
        """
        set_debug(self, debug)

        if not hasattr(items, '__iter__'):
            items = [items]

        items = map(lambda path: path.path if isinstance(path, Item) else path, items)

        result = self.rest_interface.create_share(items)
        return create_items_from_json(self.rest_interface, result, None)[0]