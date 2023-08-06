from private.cached_object import CachedObject
from private.utils import set_debug

from errors import operation_not_allowed

class Account(CachedObject):
    """
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/user-operations/
    """
    def _refresh_request(self, debug=False):
        set_debug(self, debug)
        return self.rest_interface.user_profile()

    def _initialize_self(self, request_info, x_headers={}):
        self.data = {'request':request_info, 'headers':x_headers}

    @property
    def id(self):
        """
        :setter: Disabled
        :return: Id of this users' account.
        :rtype: String
        """
        return self.data['request']['account_id']

    @property
    def storage_usage(self):
        """
        :setter: Disabled
        :return: Current storage usage of the account.
        :rtype: int
        """
        return self.data['request']['storage']['usage']

    @property
    def storage_limit(self):
        """
        :setter: Disabled
        :return: Storage limit of the current account plan.
        :rtype: int
        """
        return self.data['headers']['storage']['limit']

    @property
    def over_storage_limit(self):
        """
        :setter: Disabled
        :return: If CloudFS thinks you are currently over your storage quota.
        :rtype: Bool
        """
        return self.data['request']['storage']['otl']

    @property
    def state_display_name(self):
        """
        :setter: Disabled
        :return: Current account state.
        :rtype: String
        """
        return self.data['request']['account_state']['display_name']

    @property
    def state_id(self):
        """
        :setter: Disabled
        :return: Id of the current account state.
        :rtype: String
        """
        return self.data['request']['account_state']['id']

    @property
    def plan_display_name(self):
        """
        :setter: Disabled
        :return: Human readable name of the accounts' CloudFS plan
        :rtype: String
        """
        return self.data['request']['account_plan']['display_name']

    @property
    def plan_id(self):
        """
        :setter: Disabled
        :return: Id of the CloudFS plan.
        :rtype: String
        """
        return self.data['request']['account_plan']['id']

    @property
    def session_locale(self):
        """
        :Setter: Disabled
        :return: Locale of the current session.
        :rtype: String
        """
        return self.data['request']['session']['locale']

    @session_locale.setter
    def session_locale(self, new_locale):
        raise operation_not_allowed('set session locale')

    @property
    def locale(self):
        """
        :Setter: Disabled
        :return: Locale of the account.
        :rtype: String
        """
        return self.data['request']['locale']

    @locale.setter
    def locale(self, new_locale):
        raise operation_not_allowed('set account locale')

    @id.setter
    def id(self, new_id):
        raise operation_not_allowed('set account id')

    @state_display_name.setter
    def state_display_name(self, new_state_string):
        raise operation_not_allowed('set account state string')

    @state_id.setter
    def state_id(self, new_state_id):
        raise operation_not_allowed('set account state id')

    @plan_display_name.setter
    def plan_display_name(self, new_plan):
        raise operation_not_allowed('Changing the a plan through the API')

    @plan_id.setter
    def plan_id(self, new_plan_id):
        raise operation_not_allowed('set account plan id')

    @over_storage_limit.setter
    def over_storage_limit(self, new_otl_flag):
        raise operation_not_allowed('set over the limit flag')

    @storage_usage.setter
    def storage_usage(self, new_usage):
        raise operation_not_allowed('Setting usage through the API')

    @storage_limit.setter
    def storage_limit(self, new_quota):
        raise operation_not_allowed('Setting the storage limit through the API')
