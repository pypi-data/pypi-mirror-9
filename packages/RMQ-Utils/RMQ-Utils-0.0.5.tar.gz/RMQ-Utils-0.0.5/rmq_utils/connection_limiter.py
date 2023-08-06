from time import sleep
from common import connect_to_management_api


class ConnectionLimiter(object):

    def __init__(self, mgmt_host, mgmt_user, mgmt_password):
        self._management_api = connect_to_management_api(mgmt_host, mgmt_user, mgmt_password)

    def _open_connections_by_user(self):
        output = {}
        for c in self._management_api.get_connections():
            try:
                output[c['user']].append(c['name'])
            except KeyError:
                output[c['user']] = [c['name']]
        return output

    def _close_connections(self, connection_names):
        for name in connection_names:
            self._management_api.delete_connection(name)

    @staticmethod
    def max_connections_by_user():
        raise NotImplementedError('Must implement method: max_connections_by_user')

    def run(self, wait):
        while True:
            open_connections_by_user = self._open_connections_by_user()
            max_connections_by_user = self.max_connections_by_user()
            for user, connections in open_connections_by_user.iteritems():
                connection_count = len(connections)
                max_allowed = max_connections_by_user[user]
                if connection_count > max_allowed:
                    self._close_connections(connections[:connection_count - max_allowed])
            sleep(wait * 0.001)
