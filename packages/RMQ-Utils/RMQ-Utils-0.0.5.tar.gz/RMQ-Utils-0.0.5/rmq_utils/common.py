from pyrabbit.api import Client

from exceptions import InvalidUser


def connect_to_management_api(host, user, password):
    client = Client(host, user, password)
    if not client.has_admin_rights:
        raise InvalidUser('User must have admin rights')
    return client
