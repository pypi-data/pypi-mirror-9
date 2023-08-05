"""
Packet management

"""

from dataplicity.m2m import bencode
from dataplicity.compat import int_types, text_type


class PacketError(Exception):
    """A packet format error"""


class PacketFormatError(PacketError):
    """Packet is badly formatted"""
    pass


class UnknownPacketError(PacketError):
    """A packet we don't know how to handle"""
    pass


class PacketMeta(type):
    """Maintains a registry of packet classes"""

    def __new__(mcs, name, bases, attrs):
        packet_cls = super(PacketMeta, mcs).__new__(mcs, name, bases, attrs)
        if bases[0] is not object:
            if packet_cls.type >= 0:
                assert packet_cls.type not in packet_cls.registry, "packet type {!r} has already been registered".format(packet_cls, type)
                packet_cls.registry[packet_cls.type] = packet_cls
        return packet_cls


class PacketBase(object):
    __metaclass__ = PacketMeta

    registry = {}

    # Packet type
    type = -1  # Indicates it is a base packet class

    # Named attributes, if using default init_data
    attributes = []

    def __init__(self, *args, **kwargs):
        self.init_params(args, kwargs)
        self.validate()

    def __repr__(self):
        data = {}
        for attrib_name, attrib_type in self.attributes:
            try:
                data[attrib_name] = getattr(self, attrib_name)
            except AttributeError:
                continue

        params = ', '.join("{}={!r}".format(k, v) for k, v in data.items())
        return "{}({})".format(self.__class__.__name__, params)

    def process_packet_type(self, packet_type):
        return packet_type

    @classmethod
    def create(cls, packet_type, *args, **kwargs):
        """Dynamically create a packet from its type and parameters"""
        packet_cls = cls.registry.get(cls.process_packet_type(packet_type))
        return packet_cls(*args, **kwargs)

    @classmethod
    def from_bytes(cls, packet_bytes):
        """Return a packet from a bytes string"""
        try:
            packet_data = bencode.decode(packet_bytes)
        except bencode.DecodeError as e:
            raise PacketFormatError('packet is badly formated ({!r})'.format(e))

        if not isinstance(packet_data, list):
            raise PacketFormatError('packet must be a list')
        packet_type = packet_data[0]
        if not isinstance(packet_type, int_types):
            raise PacketFormatError('first value must be an integer')
        packet_body = packet_data[1:]
        try:
            packet_cls = cls.registry[packet_type]
        except:
            raise UnknownPacketError("unknown packet type '{}'".format(packet_type))
        return packet_cls.from_body(packet_body)

    @classmethod
    def from_body(cls, packet_body):
        """Return a packet object from a packet body"""
        params = {}
        for (attrib_name, attrib_type), value in zip(cls.attributes, packet_body):
            params[attrib_name] = value
        return cls(**params)

    @property
    def kwargs(self):
        return {attrib_name: getattr(self, attrib_name)
                for attrib_name, attrib_type in self.attributes}

    def get_method_args(self, arg_count):
        args = []
        kwargs = self.kwargs.copy()
        for attrib_name, _ in self.attributes[:arg_count]:
            args.append(kwargs.pop(attrib_name))
        return args, kwargs

    def init_params(self, args, kwargs):
        """Initialize from parameters"""
        # Default implementation copies named attributes

        params = {}

        for arg, (attribute_name, attrib_type) in zip(args, self.attributes):
            if isinstance(arg, text_type):
                arg = arg.encode('utf-8')
            params[attribute_name] = arg
        for k, v in kwargs.items():
            if isinstance(v, text_type):
                v = v.encode('utf-8')
            params[k] = v

        for attrib_name, attrib_type in self.attributes:
            if attrib_name not in params:
                raise PacketFormatError("missing attribute '{}', in {!r}".format(attrib_name, self))
            value = params[attrib_name]
            if attrib_type is not None and not isinstance(value, attrib_type):
                raise PacketFormatError("parameter '{}' should be a {!r}, in {!r} (not {!r})".format(attrib_name, attrib_type, self, type(value)))
            setattr(self, attrib_name, params[attrib_name])

    def validate(self):
        """Check packet data for errors"""
        pass

    @property
    def as_bytes(self):
        """packet as bytes"""
        return self.encode_binary()

    def encode_binary(self):
        """Encode the packet in to a byte string"""
        return bencode.encode(self.encode())

    def encode(self):
        """Encode the packet (including type header)"""
        data = ([int(self.type)] +
                [getattr(self, attrib_name) for attrib_name, attrib_type in self.attributes])
        return data
