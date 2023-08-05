"""Code common to Connection and Channel objects
"""
from abc import ABCMeta, abstractmethod
from threading import Lock

from .proto import Method
from .exceptions import AMQPNotImplementedError, RecoverableConnectionError
from . import spec

__all__ = ['AbstractChannel']


class AbstractChannel(metaclass=ABCMeta):
    """Superclass for both the Connection, which is treated as channel 0, and other user-created
    Channel objects

    The subclasses must have a METHOD_MAP class variable, mapping between AMQP method signatures and
    Python methods.
    """

    #: Placeholder, implementations must override this
    METHOD_MAP = {}

    #: List of methods which must be handled immediately
    IMMEDIATE_METHODS = [spec.Basic.Return]

    def __init__(self, connection, channel_id):
        """
        :type connection: amqpy.connection.Connection
        :type channel_id: int
        """
        self.connection = connection
        self.channel_id = channel_id
        connection.channels[channel_id] = self
        # queue of incoming methods for this channel
        self.method_queue = []  # list[Method]
        self.auto_decode = False
        self.lock = Lock()

    @abstractmethod
    def close(self):
        """Close this Channel or Connection
        """
        pass

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _send_method(self, method):
        if self.connection is None:
            raise RecoverableConnectionError('connection already closed')

        if method.channel_id is None:
            method.channel_id = self.channel_id
        self.connection.method_writer.write_method(method)

    def wait(self, method=None):
        """Wait for the specified method from the server

        :param method: method to wait for, or `None` to wait for any method
        :type method: spec.method_t or None
        """
        m = self._wait_method([method])
        return self.handle_method(m)

    def wait_any(self, allowed_methods):
        """Wait for a method that matches any one of `allowed_methods`

        :param allowed_methods: list of methods to wait for
        :type allowed_methods: list[spec.method_t]
        """
        m = self._wait_method(allowed_methods)
        return self.handle_method(m)

    def _wait_method(self, allowed_methods):
        """Wait for a method from the server destined for the current channel

        This method is designed to be called from a channel instance.

        :return: method
        :rtype: Method
        """
        # create a more convenient list of methods to check
        if isinstance(allowed_methods, list):
            # we should always check if the incoming method is a channel or connection close
            allowed_methods = [spec.Channel.Close, spec.Connection.Close] + allowed_methods

        # check the channel's method queue
        method_queue = self.connection.channels[self.channel_id].method_queue

        for qm in method_queue:
            assert isinstance(qm, Method)
            if allowed_methods is None or qm.method_type in allowed_methods:
                # found the method we're looking for in the queue
                method_queue.remove(qm)
                return qm

        # nothing queued, need to wait for a method from the server
        while True:
            method = self.connection.method_reader.read_method()
            ch_id = method.channel_id
            m_type = method.method_type

            # check if the received method is the one we're waiting for
            if method.channel_id == self.channel_id and (allowed_methods is None
                                                         or m_type in allowed_methods):
                # received the method we're waiting for
                return method

            # check if the received method needs to be handled immediately
            if ch_id != 0 and m_type in self.IMMEDIATE_METHODS:
                # certain methods like basic_return should be dispatched immediately rather than
                # being queued, even if they're not one of the `allowed_methods` we're looking for
                self.connection.channels[ch_id].handle_method(method)
                continue

            # not the channel and/or method we were looking for; queue this method for later
            self.connection.channels[ch_id].method_queue.append(method)

            # if the method is destined for channel 0 (the connection itself), it's probably an
            # exception, so handle it immediately
            if ch_id == 0:
                self.connection.wait()

    def handle_method(self, method, channel=None):
        """Handle the specified received method

        The appropriate handler as defined in `self.METHOD_MAP` will be called to handle this
        method.

        :param method: freshly received method from the server
        :param channel: channel object
        :type method: amqpy.proto.Method
        :type channel: amqpy.channel.Channel or None
        :return: the return value of the specific callback or method handler
        """
        #: :type: GenericContent
        content = method.content
        channel = channel or self

        if content and channel.auto_decode and 'content_encoding' in content.properties:
            # try to decode message body
            # noinspection PyBroadException
            try:
                content.body = content.body.decode(content.properties['content_encoding'])
            except Exception:
                pass

        try:
            callback = channel.METHOD_MAP[method.method_type]
        except KeyError:
            raise AMQPNotImplementedError('Unknown AMQP method {0}'.format(method.method_type))

        return callback(channel, method)
