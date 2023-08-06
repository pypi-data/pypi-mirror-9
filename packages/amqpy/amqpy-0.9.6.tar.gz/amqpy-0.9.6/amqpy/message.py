"""Messages for AMQP
"""
from . import spec
from amqpy.serialization import AMQPReader, AMQPWriter

__all__ = ['Message']


class GenericContent:
    """Base class for AMQP content

    Subclasses should override :attr:`PROPERTIES`.
    """
    PROPERTIES = []

    def __init__(self, properties):
        """Save the properties appropriate to this AMQP content type in a 'properties' dictionary

        :param dict properties: content properties
        """
        #: Content properties
        #:
        #: :type: dict[str, str|dict]
        self.properties = properties

    def __eq__(self, other):
        """Check if this object has the same properties as another content object
        """
        return self.properties == other.properties

    def load_properties(self, raw_bytes):
        """Load raw bytes into :attr:`self.properties`

        The `raw_bytes` are the payload of a `FrameType.HEADER` frame, starting at a byte-offset
        of 12.
        """
        r = AMQPReader(raw_bytes)

        # read 16-bit shorts until we get one with a low bit set to zero
        flags = []
        while True:
            flag_bits = r.read_short()
            flags.append(flag_bits)
            if flag_bits & 1 == 0:
                break

        shift = 0
        d = {}
        flag_bits = None
        for key, proptype in self.PROPERTIES:
            if shift == 0:
                if not flags:
                    break
                flag_bits, flags = flags[0], flags[1:]
                shift = 15
            if flag_bits & (1 << shift):
                d[key] = getattr(r, 'read_' + proptype)()
            shift -= 1

        self.properties = d

    def serialize_properties(self):
        """Serialize :attr:`self.properties` into raw bytes suitable to append to the payload of
        `FrameType.HEADER` frames
        """
        shift = 15
        flag_bits = 0
        flags = []
        raw_bytes = AMQPWriter()
        for key, proptype in self.PROPERTIES:
            val = self.properties.get(key, None)
            if val is not None:
                if shift == 0:
                    flags.append(flag_bits)
                    flag_bits = 0
                    shift = 15

                flag_bits |= (1 << shift)
                if proptype != 'bit':
                    getattr(raw_bytes, 'write_' + proptype)(val)

            shift -= 1

        flags.append(flag_bits)
        result = AMQPWriter()
        for flag_bits in flags:
            result.write_short(flag_bits)
        result.write(raw_bytes.getvalue())

        return result.getvalue()


class Message(GenericContent):
    """A Message for use with the `Channel.basic_*` methods
    """
    CLASS_ID = spec.Basic.CLASS_ID

    # instances of this class have these attributes, which are passed back and forth as message
    # properties between client and server
    PROPERTIES = [
        ('content_type', 'shortstr'),
        ('content_encoding', 'shortstr'),
        ('application_headers', 'table'),
        ('delivery_mode', 'octet'),
        ('priority', 'octet'),
        ('correlation_id', 'shortstr'),
        ('reply_to', 'shortstr'),
        ('expiration', 'shortstr'),
        ('message_id', 'shortstr'),
        ('timestamp', 'timestamp'),
        ('type', 'shortstr'),
        ('user_id', 'shortstr'),
        ('app_id', 'shortstr'),
        ('cluster_id', 'shortstr')
    ]

    def __init__(self, body='', channel=None, **properties):
        """
        If `body` is a `str`, then `content_encoding` will automatically be set to 'UTF-8', unless
        explicitly specified.

        Example::

            msg = Message('hello world', content_type='text/plain', application_headers={'foo': 7})

        :param body: message body
        :param channel: associated channel
        :param properties:
            * content_type (shortstr): MIME content type
            * content_encoding (shortstr): MIME content encoding
            * application_headers: (table): Message header field table:
              dict[str, str|int|Decimal|datetime|dict]
            * delivery_mode: (octet): Non-persistent (1) or persistent (2)
            * priority (octet): The message priority, 0 to 9
            * correlation_id (shortstr) The application correlation identifier
            * reply_to (shortstr) The destination to reply to
            * expiration (shortstr): Message expiration specification
            * message_id (shortstr): The application message identifier
            * timestamp (datetime.datetime): The message timestamp
            * type (shortstr): The message type name
            * user_id (shortstr): The creating user id
            * app_id (shortstr): The creating application id
            * cluster_id (shortstr): Intra-cluster routing identifier
        :type body: bytes or str
        :type channel: amqpy.channel.Channel
        """
        super().__init__(properties)

        #: Message body (bytes or str)
        self.body = body

        #: Associated channel, set after receiving a message (amqpy.channel.Channel)
        self.channel = channel

        #: Delivery info, set after receiving a message (dict)
        self.delivery_info = {}

        if isinstance(body, str):
            self.properties['content_encoding'] = properties.get('content_encoding', 'UTF-8')

    def __eq__(self, other):
        """Check if the properties and bodies of this Message and another Message are the same

        Received messages may contain a 'delivery_info' attribute, which isn't compared.
        """
        try:
            return super().__eq__(other) and self.body == other.body
        except AttributeError:
            return False

    @property
    def application_headers(self):
        """Get application headers

        :return: application headers
        :rtype: dict
        """
        return self.properties.get('application_headers')

    @property
    def delivery_tag(self):
        """Get delivery tag

        :return: delivery tag
        :rtype: int
        """
        return self.delivery_info.get('delivery_tag')

    def ack(self):
        """Acknowledge message

        This is a convenience method which calls :meth:`self.channel.basic_ack()`
        """
        dt = self.delivery_tag
        if dt is not None:
            self.channel.basic_ack(dt)
        else:
            raise Exception('No delivery tag')

    def reject(self, requeue):
        """Reject message

        This is a convenience method which calls :meth:`self.channel.basic_reject()`

        :param bool requeue: requeue if True else discard the message
        """
        dt = self.delivery_tag
        if dt is not None:
            self.channel.basic_reject(dt, requeue)
        else:
            raise Exception('No delivery tag')
