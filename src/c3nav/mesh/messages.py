import struct
from dataclasses import dataclass, field, fields

NO_LAYER = 0xFF
MAC_FMT = '%02x:%02x:%02x:%02x:%02x:%02x'


class SimpleFormat:
    def __init__(self, fmt):
        self.fmt = fmt
        self.size = struct.calcsize(fmt)

    def encode(self, value):
        return struct.pack(self.fmt, value)

    def decode(self, data: bytes):
        return struct.unpack(self.fmt, data[:self.size]), data[self.size:]


class VarStrFormat:
    def encode(self, value: str) -> bytes:
        return bytes((len(value)+1, )) + value.encode() + bytes((0, ))

    def decode(self, data: bytes):
        return data[1:data[0]].decode(), data[data[0]+1:]


class MacAddressFormat:
    def encode(self, value: str) -> bytes:
        return bytes(int(value[i*3:i*3+2], 16) for i in range(6))

    def decode(self, data: bytes):
        return (MAC_FMT % tuple(data[:6])), data[6:]


class MacAddressesListFormat:
    def encode(self, value: list[str]) -> bytes:
        return bytes((len(value), )) + sum(
            (bytes((int(mac[i*3:i*3+2], 16) for i in range(6))) for mac in value),
            b''
        )

    def decode(self, data: bytes):
        return [MAC_FMT % tuple(data[1+6*i:1+6+6*i]) for i in range(data[0])], data[1+data[0]*6]


@dataclass
class Message:
    msg_types = {}

    # noinspection PyMethodOverriding
    def __init_subclass__(cls, /, msg_id=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if msg_id:
            cls.msg_id = msg_id
            Message.msg_types[msg_id] = cls

    def encode(self):
        data = bytes((self.msg_id, ))
        for field_ in fields(self):
            data += field_.metadata['format'].encode(getattr(self, field_.name))
        return data

    @classmethod
    def decode(cls, data: bytes):
        klass = cls.msg_types[data[0]]
        data = data[1:]
        values = {}
        for field_ in fields(klass):
            values[field_.name], data = field_.metadata['format'].decode(data)
        return klass(**values)


@dataclass
class EchoMessage(Message, msg_id=0x01):
    content: str = field(default='', metadata={'format': VarStrFormat()})


@dataclass
class MeshSigninMessage(Message, msg_id=0x02):
    mac_address: str = field(metadata={'format': MacAddressFormat()})


@dataclass
class MeshLayerAnnounceMessage(Message, msg_id=0x03):
    layer: int = field(metadata={'format': SimpleFormat('B')})


@dataclass
class BaseMeshDestinationsMessage(Message):
    mac_addresses: list[str] = field(default_factory=list, metadata={'format': MacAddressesListFormat()})


@dataclass
class MeshAddDestinationsMessage(BaseMeshDestinationsMessage, msg_id=0x04):
    pass


@dataclass
class MeshRemoveDestinationsMessage(BaseMeshDestinationsMessage, msg_id=0x05):
    pass
