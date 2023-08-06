from private.cached_object import CachedObject
from private.utils import set_debug

from errors import operation_not_allowed, method_not_implemented

class User(CachedObject):
    """
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/user-operations/
    """
    def _refresh_request(self, debug=False):
        set_debug(self, debug)
        return self.rest_interface.user_profile()

    @property
    def email(self):
        """
        :setter: Disabled
        :return: User email.
        :rtype:  String
        """
        return self._get('email', '')

    @property
    def first_name(self):
        """
        :setter: Disabled
        :return: User first name.
        :rtype:  String
        """
        return self._get('first_name', '')

    @property
    def last_name(self):
        """
        :setter: Disabled
        :return: User last name.
        :rtype:  String
        """
        return self._get('last_name', '')

    @property
    def id(self):
        """
        :setter: Disabled
        :return: User id
        :rtype:  String
        """
        return self._get('id', '')

    @property
    def username(self):
        """
        :setter: Disabled
        :return: User's username, often an email.
        :rtype:  String
        """
        return self._get('username', '')

    # unlike file times, these are in milliseconds
    @property
    def last_login(self):
        """
        :setter: Disabled
        :return: Last login time.
        :rtype:  milliseconds in int.
        """
        return self._get('last_login', 0)

    # unlike file times, these are in milliseconds
    @property
    def created_at(self):
        """
        :setter: Disabled
        :return: Creation time.
        :rtype:  milliseconds in int.
        """
        return self._get('created_at', 0)

    @email.setter
    def email(self, new_email):
        raise method_not_implemented(self, 'set user email')

    @first_name.setter
    def first_name(self, new_first_name):
        raise method_not_implemented(self, 'set user first name')

    @last_name.setter
    def last_name(self, new_last_name):
        raise method_not_implemented(self, 'set user last name')

    @id.setter
    def id(self, new_id):
        raise operation_not_allowed('Changing a users id')

    @username.setter
    def username(self, new_username):
        raise operation_not_allowed('Changing a users username')

    @last_login.setter
    def last_login(self, new_last_login):
        raise operation_not_allowed('Setting a users last login time')

    @created_at.setter
    def created_at(self, new_created_at):
        raise operation_not_allowed('Setting a the time a user was created')

    def save(self):
        raise method_not_implemented('User', 'save changes')


    def __str__(self):
        names = ''
        if self.first_name != '' or self.last_name != '':
            names = '{},{}'.format(self.first_name, self.last_name)
        return "User:{}{} {}".format(
            self.username,
            '({})'.format(self.email) if self.email != '' else '',
            names
        )