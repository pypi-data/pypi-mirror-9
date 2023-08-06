from private.rest_api_adapter import CloudFSRESTAdapter
from private.utils import set_debug

from user import User
from account import Account
from filesystem import Filesystem
from errors import operation_not_allowed


class Session(object):
    """
    REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/authentication-operations/
    """
    def __init__(self, endpoint, client_id, client_secret):
        """ Create a new session object for a particular application

        :param endpoint:        Api endpoint for your cloudfs account (i.e. xxxxxxxxxx.cloudfs.io).
        :param client_id:       Client Id, found by clicking on an application on your user control panel.
        :param client_secret:   Client Secret, found by clicking on an application on your user control panel.
        :return:                A un-authenticated cloudfs session.
        :rtype:                 Session object
        """
        self.rest_interface = CloudFSRESTAdapter(endpoint, client_id, client_secret)
        self.admin_rest_interface = None
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret

    # are we associated with an account?
    def is_linked(self, debug=False):
        """ Can this session make requests?

        :param debug:   If true, will print the the request and response to stdout.
        :return:        True if this session is currently authenticated, false otherwise.
        :rtype: Bool
        """
        set_debug(self, debug)
        return self.rest_interface.is_linked()

    # set any account credentials to nil
    def unlink(self):
        """ Discard current authentication.

        :return: None
        """
        self.rest_interface.unlink()

    def set_access_token(self, access_token):
        self.rest_interface.bc_conn.set_access_token(access_token)

    def set_admin_credentials(self, admin_client_id, admin_client_secret, admin_endpoint='access.bitcasa.com'):
        """Set the credentials used for creating users.

        :note: The client id and secret here are different from your application's id and secret. They are only available to CloudFS accounts above the "Prototype" tier.

        :param admin_client_id: Client id for your admin API server .
        :param admin_secret:    Client secret for your admin API server.
        :param admin_endpoint:  Endpoint for admin calls. Optional, defaults to access.bitcasa.com.
        :return:                None
        :raise ValueError:      Will be raised
        """
        if admin_client_id == self.client_id:
            raise ValueError("Admin Id cannot be the same as client id!")
        self.admin_rest_interface = CloudFSRESTAdapter(admin_endpoint, admin_client_id, admin_client_secret)

    def create_account(self, username, password, email=None, first_name=None, last_name=None, log_in_to_created_user=False, debug=False):
        """Create a user account associated with your CloudFS account.

        :note: Although this method creates a User object - the session associated with the user is _not_ linked. You must authenticate it before using it.

        REST Documentation: https://developer.bitcasa.com/cloudfs-rest-documentation/administration-operations/

        :param username:                Username for the user, must be at least 4 characters and less than 256 characters.
        :param password:                Password for the user, must be at least 6 characters and has no length limit.
        :param email:                   Email address for user. Optional.
        :param first_name:              Users' first name. Optional
        :param last_name:               Users' last name. Optional
        :param log_in_to_created_user:  If True, will log into the created user account in this session. Optional, defaults to False.
        :param debug:                   If True, will print the the request and response to stdout.
        :return:                        Newly created User.
        :rtype:                         User object.
        :raise OperationNotAllowed:
        """
        if not self.admin_rest_interface:
            raise operation_not_allowed("Account creation without admin credentials")

        if debug:
            self.admin_rest_interface.debug_requests(1)

        response = self.admin_rest_interface.create_account(username, password, email, first_name, last_name)
        if log_in_to_created_user:
            self.authenticate(username, password, debug)
        return User(self.rest_interface.get_copy(),
                    response)

    # link this session to an account
    def authenticate(self, username, password, debug=False):
        """ Attempt to log into the given users' filesystem.

        :param username:    Username of the user.
        :param password:    Password of the user.
        :param debug:       If true, will print the the request and response to stdout.
        :return:            True if successful, False otherwise.
        :rtype:             Bool
        """
        set_debug(self, debug)
        return self.rest_interface.authenticate(username, password)

    def user(self, debug=False):
        """Get an object describing the current user.

        :param debug:   If true, will print the the request and response to stdout.
        :return:        The current user.
        :rtype:         User object
        """
        set_debug(self, debug)

        return User(self.rest_interface.get_copy(),
                    self.rest_interface.user_profile())


    def action_history(self, start_version=-10, stop_version=None, debug=False):
        """List previous actions taken by the current user.

        See CloudFSRESTAdapter documentation for notes on using this.

        :param start_version:           First version number to list. If negative, will be treated as a limit on number of actions. Optional, defaults to -10.
        :param stop_version:            Version number to stop listing at. Not the count of actions. Optional, defaults to none.
        :return:                        List of actions on the filesystem.
        :rtype:                         List of dictionaries
        :raises SessionNotLinked:       CloudFSRESTAdapter is not authenticated.
        :raises AuthenticatedError:     Based on CloudFS Error Code.
        """
        set_debug(self, debug)

        return self.rest_interface.action_history(start_version, stop_version)

    def account(self, debug=False):
        """Get an object describing the current users account.

        :param debug:   If true, will print the the request and response to stdout.
        :return:        Current user account.
        :rtype:         Account object
        """
        set_debug(self, debug)

        return Account(self.rest_interface.get_copy(),
                       self.rest_interface.user_profile())


    def filesystem(self):
        """ Get a filesystem object.

        Does not use a request.

        :return: Filesystem object linked to this session.
        """
        return Filesystem(self.rest_interface.get_copy())