import json

from mixins import AsyncConsumer
from common import connect_to_management_api


class AccountDestroyer(AsyncConsumer):

    def __init__(self, rabbit_url, mgmt_host, mgmt_user, mgmt_password):
        super(AccountDestroyer, self).__init__(
            rabbit_url=rabbit_url,
            queue='account_destroyer',
            exchange='rmq_utils',
            exchange_type='direct',
            routing_key='account_destroyer')
        self._management_api = connect_to_management_api(mgmt_host, mgmt_user, mgmt_password)

    def _delete_rabbit_account(self, username):
        self._management_api.delete_user(username)
        self._management_api.delete_vhost(username)

    @staticmethod
    def post_delete(key, creds):
        """This method gets called after each successful call to the `_delete_rabbit_account` method."""
        raise NotImplementedError('Must implement method: post_delete')

    def _on_message(self, unused_channel, basic_deliver, properties, body):
        message = json.loads(body)
        user_key = message['user_key']
        username = message['rabbit_user']
        self._delete_rabbit_account(username)
        self.post_delete(user_key)
        self._acknowledge_message(basic_deliver.delivery_tag)
