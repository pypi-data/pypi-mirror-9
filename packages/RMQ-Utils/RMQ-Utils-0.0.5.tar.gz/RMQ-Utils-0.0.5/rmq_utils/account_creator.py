import json
import random
import string

from mixins import AsyncConsumer
from common import connect_to_management_api


class AccountCreator(AsyncConsumer):

    def __init__(self, rabbit_url, mgmt_host, mgmt_user, mgmt_password):
        super(AccountCreator, self).__init__(
            rabbit_url=rabbit_url,
            queue='account_creator',
            exchange='rmq_utils',
            exchange_type='direct',
            routing_key='account_creator')
        self._management_api = connect_to_management_api(mgmt_host, mgmt_user, mgmt_password)

    @staticmethod
    def _random_string(size=6):
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(size)])

    def _create_rabbit_account(self):
        username = self._random_string(8)
        password = self._random_string(32)
        vhost = username

        self._management_api.create_user(username, password)
        self._management_api.create_vhost(vhost)
        self._management_api.set_vhost_permissions(vhost, username, ".*", ".*", ".*")

        return {
            'username': username,
            'password': password,
            'vhost': vhost
        }

    @staticmethod
    def post_create(key, creds):
        """This method gets called after each successful call to the `_create_rabbit_account` method."""
        raise NotImplementedError('Must implement method: post_create')

    def _on_message(self, unused_channel, basic_deliver, properties, body):
        message = json.loads(body)
        user_key = message['user_key']
        creds = self._create_rabbit_account()
        self.post_create(user_key, creds)
        self._acknowledge_message(basic_deliver.delivery_tag)
