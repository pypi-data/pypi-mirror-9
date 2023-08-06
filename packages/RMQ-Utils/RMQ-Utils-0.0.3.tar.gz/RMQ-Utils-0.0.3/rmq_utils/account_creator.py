import random
import string
from time import sleep
from pyrabbit.api import Client

from exceptions import InvalidUser


class AccountCreator(object):

    def __init__(self, host, user, password, wait):
        self._host = host
        self._user = user
        self._password = password
        self._wait = wait * 0.001
        self._management_api = self._connect_to_management_api()

    def _connect_to_management_api(self):
        client = Client(self._host, self._user, self._password)
        if not client.has_admin_rights:
            raise InvalidUser('User must have admin rights')
        return client

    @staticmethod
    def _random_string(size=6):
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(size)])

    def _create_rabbit_account(self):
        username = self._random_string(8)
        password = self._random_string(32)

        self._management_api.create_user(username, password)
        self._management_api.create_vhost(username)
        self._management_api.set_vhost_permissions(username, username, ".*", ".*", ".*")

        return {
            'username': username,
            'password': password,
            'vhost': username
        }

    @staticmethod
    def accounts_to_create():
        """This should return a list of keys (string) representing each user to be created. \
        Once created the key, and new user creds will be passed into the `accounts_post_create` \
        method
        """
        raise NotImplementedError('Must implement method: accounts_to_create')

    @staticmethod
    def accounts_post_create(key, creds):
        """This method gets called after each successful call to the `_create_rabbit_account` method."""
        raise NotImplementedError('Must implement method: accounts_post_create')

    def start(self):
        while True:
            for user_key in self.accounts_to_create():
                creds = self._create_rabbit_account()
                self.accounts_post_create(user_key, creds)
            sleep(self._wait)
