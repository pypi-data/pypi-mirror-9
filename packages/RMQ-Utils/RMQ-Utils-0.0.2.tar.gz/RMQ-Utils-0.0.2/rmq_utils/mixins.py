import logging
import pika

from pyrabbit.api import Client
from urlparse import urlparse

from exceptions import InvalidConnectionURL, InvalidUser

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


class ManagementAPI(object):

    def _validate_connection_url(self):
        parsed = urlparse(self._url)
        if parsed.hostname != 'localhost':
            raise InvalidConnectionURL('Connection allowed to localhost only')
        return parsed

    def _connect_to_management_api(self, port):
        parsed = self._validate_connection_url()
        host = '{0}:{1}'.format(parsed.hostname, port)
        user = parsed.username
        password = parsed.password
        client = Client(host, user, password)
        if not client.has_admin_rights:
            raise InvalidUser('User must have admin rights')
        return client

    def post_create_handler(self, user_key, user_creds):
        raise NotImplementedError('Method post_create_handler must be implemented')


class AsyncConsumer(object):

    def __init__(self, rabbit_url):
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = rabbit_url

    def _connect(self):
        log_message = 'Connecting to Rabbit URL'
        LOGGER.info(log_message)

        return pika.SelectConnection(
            pika.URLParameters(self._url),
            self._on_connection_open,
            stop_ioloop_on_close=False)

    def _close_connection(self):
        log_message = 'Closing connection'
        LOGGER.info(log_message)

        self._connection.close()

    def _add_on_connection_close_callback(self):
        self._connection.add_on_close_callback(self._on_connection_closed)

    def _on_connection_closed(self, connection, reply_code, reply_text):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            log_message = 'Connection closed, reopening in 5 seconds: ({0}) {1}'.format(reply_code, reply_text)
            LOGGER.warning(log_message)

            self._connection.add_timeout(5, self._reconnect)

    def _on_connection_open(self, unused_connection):
        log_message = 'Connection opened'
        LOGGER.info(log_message)

        self._add_on_connection_close_callback()
        self._open_channel()

    def _reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self._connect()
            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def _add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self._on_channel_closed)

    def _on_channel_closed(self, channel, reply_code, reply_text):
        log_message = 'Channel {0} was closed: ({1}) {2}'.format(channel, reply_code, reply_text)
        LOGGER.warning(log_message)

        self._connection.close()

    def _on_channel_open(self, channel):
        log_message = 'Channel opened'
        LOGGER.info(log_message)

        self._channel = channel
        self._add_on_channel_close_callback()
        self._setup_exchange(self.EXCHANGE)

    def _setup_exchange(self, exchange_name):
        log_message = 'Declaring exchange {0}'.format(exchange_name)
        LOGGER.info(log_message)

        self._channel.exchange_declare(
            self._on_exchange_declareok,
            exchange_name,
            self.EXCHANGE_TYPE)

    def _on_exchange_declareok(self, unused_frame):
        log_message = 'Exchange declared'
        LOGGER.info(log_message)

        self._setup_queue(self.QUEUE)

    def _setup_queue(self, queue_name):
        log_message = 'Declaring queue {0}'.format(queue_name)
        LOGGER.info(log_message)

        self._channel.queue_declare(self._on_queue_declareok, queue_name)

    def _on_queue_declareok(self, method_frame):
        log_message = 'Binding {0} to {1} with {2}'.format(self.EXCHANGE, self.QUEUE, self.ROUTING_KEY)
        LOGGER.info(log_message)

        self._channel.queue_bind(
            self._on_bindok,
            self.QUEUE,
            self.EXCHANGE,
            self.ROUTING_KEY)

    def _add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self._on_consumer_cancelled)

    def _on_consumer_cancelled(self, method_frame):
        log_message = 'Consumer was cancelled remotely, shutting down: {0}'.format(method_frame)
        LOGGER.info(log_message)

        if self._channel:
            self._channel.close()

    def _acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)

    # def _on_message(self, unused_channel, basic_deliver, properties, body):
    #     log_message = 'Received message # %s from %s: %s'
    #     LOGGER.info(log_message, basic_deliver.delivery_tag, properties.app_id, body)

    #     self._acknowledge_message(basic_deliver.delivery_tag)

    def _on_cancelok(self, unused_frame):
        log_message = 'RabbitMQ acknowledged the cancellation of the consumer'
        LOGGER.info(log_message)

        self._close_channel()

    def _stop_consuming(self):
        if self._channel:
            log_message = 'Sending a Basic.Cancel RPC command to RabbitMQ'
            LOGGER.info(log_message)

            self._channel.basic_cancel(self._on_cancelok, self._consumer_tag)

    def _start_consuming(self):
        log_message = 'Start consuming'
        LOGGER.info(log_message)

        self._add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self._on_message, self.QUEUE)

    def _on_bindok(self, unused_frame):
        log_message = 'Queue bound'
        LOGGER.info(log_message)

        self._start_consuming()

    def _close_channel(self):
        log_message = 'Closing the channel'
        LOGGER.info(log_message)

        self._channel.close()

    def _open_channel(self):
        log_message = 'Creating a new channel'
        LOGGER.info(log_message)

        self._connection.channel(on_open_callback=self._on_channel_open)

    def run(self):
        self._connection = self._connect()
        self._connection.ioloop.start()

    def stop(self):
        log_message = 'Stopping'
        LOGGER.info(log_message)

        self._closing = True
        self._stop_consuming()
        self._connection.ioloop.start()

        log_message = 'Stopped'
        LOGGER.info(log_message)
