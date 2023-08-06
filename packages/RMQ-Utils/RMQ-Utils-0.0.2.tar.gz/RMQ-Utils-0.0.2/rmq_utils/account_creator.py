import random
import string
import json

from mixins import ManagementAPI, AsyncConsumer
from exceptions import InvalidMessageBody


def random_string(size=6):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(size)])


class AccountCreator(ManagementAPI, AsyncConsumer):

    def __init__(self, rabbit_url, routing_key, api_port):
        self.EXCHANGE = 'rmq_utils'
        self.EXCHANGE_TYPE = 'direct'
        self.QUEUE = 'account_creator'
        self.ROUTING_KEY = routing_key
        super(AccountCreator, self).__init__(rabbit_url=rabbit_url)
        self._management_api = self._connect_to_management_api(api_port)

    def _create_account(self):
        username = random_string(8)
        password = random_string(32)

        self._management_api.create_user(username, password)
        self._management_api.create_vhost(username)
        self._management_api.set_vhost_permissions(username, username, ".*", ".*", ".*")

        return {
            'username': username,
            'password': password,
            'vhost': username
        }

    @staticmethod
    def _parse_message_body(body):
        try:
            message = json.loads(body)
            user_key = message['user_key']
        except ValueError:
            raise InvalidMessageBody('Message body must be valid JSON')
        except KeyError:
            raise InvalidMessageBody('Message body must have a property: user_key')

        return user_key

    # override default AsyncConsumer._on_message
    def _on_message(self, unused_channel, basic_deliver, properties, body):
        try:
            user_key = self._parse_message_body(body)
        except InvalidMessageBody:
            self._acknowledge_message(basic_deliver.delivery_tag)
            raise
        user_creds = self._create_account()
        self.post_create_handler(user_key, user_creds)
        self._acknowledge_message(basic_deliver.delivery_tag)
