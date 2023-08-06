from abc import ABCMeta, abstractmethod
from threading import Thread


class AbstractConsumer(metaclass=ABCMeta):
    """
    This class provides facilities to create and manage queue consumers. To create a consumer,
    subclass this class and override the :meth:`run` method. Then, instantiate the class with the
    desired parameters and call :meth:`declare` to declare the consumer to the server.

    Example::

        class Consumer(AbstractConsumer):
            def run(self, msg: Message):
                print('Received message: {}'.format(msg.body))
                msg.ack()

        c1 = Consumer(ch, 'test.q')
        c1.declare()

        conn.drain_events()

    To take full advantage of the work queue and consumer architecture, specify `use_thread=True`
    and make sure that QOS settings are enabled for the channel or connection. This way, multiple
    consumers may be declared on the same channel, and messages will be load-balanced among them.
    """

    def __init__(self, channel, queue, consumer_tag='', no_local=False, no_ack=False,
                 exclusive=False, use_thread=False):
        """
        :param channel: channel
        :type channel: amqpy.channel.Channel
        :param str queue: queue
        :param str consumer_tag: consumer tag, local to the connection; leave blank to let server
            auto-assign a tag
        :param bool no_local: if True: do not deliver own messages
        :param bool no_ack: server will not expect an ack for each message
        :param bool exclusive: request exclusive access
        :param bool use_thread: when the consumer run() method is called, start it in a new thread
        """
        self.channel = channel
        self.queue = queue
        self.consumer_tag = consumer_tag
        self.no_local = no_local
        self.no_ack = no_ack
        self.exclusive = exclusive
        self.use_thread = use_thread

        #: Number of messages consumed (incremented automatically)
        self.consume_count = 0

    def declare(self):
        """Declare the consumer

        This method calls :meth:`~amqpy.channel.Channel.basic_consume()` internally.

        After the queue consumer is created, :attr:`self.consumer_tag` is set to the
        server-assigned consumer tag if a tag was not specified initially.
        """
        self.consumer_tag = self.channel.basic_consume(self.queue, self.consumer_tag, self.no_local,
                                                       self.no_ack, self.exclusive,
                                                       callback=self.start,
                                                       on_cancel=self.cancel_cb)

    def cancel(self):
        """Cancel the consumer
        """
        self.channel.basic_cancel(self.consumer_tag)

    @abstractmethod
    def run(self, msg):
        """Consumer callback

        This method is called when the consumer is delivered a message. This method **must** be
        overridden in the subclass.

        :param msg: received message
        :type msg: amqpy.message.Message
        """
        pass

    def cancel_cb(self, consumer_tag):
        """Consumer cancel callback

        This method is called when the consumer is cancelled. This method may be overridden in the
        subclass.

        :param str consumer_tag: consumer tag
        """
        pass

    def _run(self, msg):
        self.run(msg)
        self.consume_count += 1

    def start(self, msg):
        if self.use_thread:
            t = Thread(target=self._run, args=(msg,), name='consumer-{}'.format(self.consumer_tag))
            t.start()
        else:
            self._run(msg)
