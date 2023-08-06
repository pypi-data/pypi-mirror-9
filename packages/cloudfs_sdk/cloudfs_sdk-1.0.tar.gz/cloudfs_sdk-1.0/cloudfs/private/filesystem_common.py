import collections

from ..errors import wrong_state_for_operation, CloudFSError
from .cloudfs_paths import  RestoreValue
from ..path import Path

NORMAL = '_is_abnormal'
IN_SHARE = 'share_key'
IN_TRASH = 'in_trash'
OLD_VERSION = 'old_version'
DEAD = 'dead'
DESYNC = 'desync'


def states_not_allowed(banned_states):
    banned_states.extend([DEAD, DESYNC])
    def check_banned_states(current_state, operation):
        for state in banned_states:
            if hasattr(current_state, state):
                if getattr(current_state, state):
                    if operation in ItemState.operation_friendly_names:
                        operation = ItemState.operation_friendly_names[operation]
                    raise wrong_state_for_operation(operation, current_state.item.type, current_state.friendly_state_string())
            else:
                raise ValueError('{}({}) is not an ItemState object!'.format(current_state, type(current_state)))

    return check_banned_states

class ItemState(object):
    # inner helper class to encapsulate an Item's state and perform transformations
    # ex: alter path after trash'ing, restores, etc

    @staticmethod
    def ShareState(share_key):
        state = ItemState(None)
        state.share_key = share_key
        return state

    @staticmethod
    def TrashState():
        state = ItemState(None)
        state.in_trash = True
        return state

    @staticmethod
    def OldVersionState():
        state = ItemState(None)
        state.old_version = True
        return state

    def __init__(self, tracked_item, parent_state=None):
        self.item = tracked_item
        self.share_key = None
        self.in_trash = False
        self.old_version = False
        self.dead = False
        self.desync = False
        if parent_state:
            self.inherit_state(parent_state)

    def inherit_state(self, parent_state):
        if isinstance(parent_state, type(self)):
            self.share_key = parent_state.share_key
            self.in_trash = parent_state.in_trash
            self.old_version = parent_state.old_version
            self.dead = parent_state.dead

    @property
    def _is_abnormal(self):
        return (self.share_key != None) \
               or (self.in_trash) \
               or (self.in_trash) \
               or (self.dead) \
               or (self.desync)

    def should_change_state(self):
        return not self.dead and not self.desync

    def delete(self, commit, force, result):
        if self.should_change_state():
            if commit:
                self.dead = True
            self.in_trash = True
            new_path = Path.path_from_string('/' + self.item.id)
            app_data = self.item.application_data
            app_data[u'_bitcasa_original_path'] = str(self.item.path[:-1])
            self.item._full_path = new_path


    def restore(self, restore_method, method_argument, maintain_validity=False):
        restore_path = None
        if self.should_change_state():
            self.in_trash = False
            if restore_method == RestoreValue.fail:
                if u'_bitcasa_original_path' in self.item.application_data:
                    restore_path = self.item.application_data[u'_bitcasa_original_path']
            elif restore_method == RestoreValue.rescue:
                restore_path = str(method_argument)
            elif restore_method == RestoreValue.recreate:
                if maintain_validity:
                    root = self.item.rest_interface.list_folder('/')
                    for item in root['items']:
                        if item['name'] == method_argument:
                            restore_path = item['id']
                else:
                    self.desync = True


        if restore_path:
            restore_path = Path.path_from_string(restore_path).append(self.item)
            self.item._full_path = restore_path

    def promote(self, result):
        if self.should_change_state():
            self.old_version = False

    def move(self, dest):
        if type(dest) is str:
            dest = Path.path_from_string(dest)
        else:
            dest = dest.copy()

        dest.append(self.item.id)
        self.item._full_path = dest

    operation_friendly_names = {
        'change_attributes': 'change attributes',
        'create_folder': 'create folder',
    }

    # All operations are bannned on DEAD and DESYNC states
    ALL_STATES = [IN_SHARE, IN_TRASH, OLD_VERSION]
    operations = {
        'versions': states_not_allowed([IN_SHARE, OLD_VERSION]),
        'change_attributes': states_not_allowed(ALL_STATES),
        'create_folder': states_not_allowed(ALL_STATES),
        'restore': states_not_allowed([OLD_VERSION, IN_SHARE]),
        'promote': states_not_allowed([IN_SHARE, IN_TRASH, NORMAL]),
        'download': states_not_allowed([OLD_VERSION, IN_TRASH]),
        'download_link': states_not_allowed([OLD_VERSION, IN_TRASH]),
        'upload': states_not_allowed(ALL_STATES),
        'move': states_not_allowed(ALL_STATES),
        'copy': states_not_allowed(ALL_STATES),
        'delete': states_not_allowed([IN_SHARE, OLD_VERSION]),
        'read': states_not_allowed([OLD_VERSION, IN_TRASH]),
        'seek': states_not_allowed([OLD_VERSION, IN_TRASH]),
        'list': states_not_allowed([])
    }

    def check_operation_allowed(self, operation_name):
        if operation_name in self.operations:
            self.operations[operation_name](self, operation_name)
        else:
            assert(False)

    def friendly_state_string(self):
        state = 'normal'
        if self.share_key:
            state = 'in share'
        if self.old_version:
            state = 'previous version'
        if self.in_trash:
            state = 'in trash'
        if self.dead:
            state = 'permanently deleted'
        if self.desync:
            state = 'lost server sync'
        return '[{}]'.format(state)

    def __str__(self):
        return '[{}<{}.{}.{}.{}>]'.format(
            self.item.path if self.item else '<No Item>',
            'S' if self.share_key else '_',
            'T' if self.in_trash else '_',
            'O' if self.old_version else '_',
            'D' if self.dead else '_'
        )

def create_items_from_json(rest_interface, data, parent_path,
                           parent_state = None, allow_root=False):
    from ..file import File
    from ..container import Folder
    from ..share import Share
    if 'results' in data:
        data = data['results']

    if 'items' in data:
        data = data['items']

    items = []

    parent_item = None # root
    if parent_path and str(parent_path) != '/':

        if not parent_item:
            parent_item = parent_path

    def create_item(item_json, parent):
        new_item = None
        if 'type' not in item_json and 'share_key' in item_json:
            new_item = Share(rest_interface.get_copy(), item_json)
        elif item_json['type'] == 'folder' or (item_json['type'] == 'root' and allow_root): #file meta on root
            new_item = Folder(rest_interface.get_copy(), item_json, parent, parent_state=parent_state)
        elif item_json['type'] == 'file':
            new_item = File(rest_interface.get_copy(), item_json, parent, parent_state=parent_state)
        elif item_json['type'] == 'root': #lolololololol
            # sometimes you can end up having a root object added to your root.
            # Yo Dawg
            return
        else:
            raise CloudFSError('Did not recognize item from JSON: {}'.format(item_json))

        items.append(new_item)


    # single item from upload / etc
    if isinstance(data, collections.Mapping):
        create_item(data, parent_item)
    else:
        # directory listing
        for item in data:
            create_item(item, parent_item)


    return items
