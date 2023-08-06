"""
This package imports the codecs that can be used for de- and encoding incoming
and outgoing messages:

- :class:`JSON` uses `JSON <http://www.json.org/>`_
- :class:`MsgPack` uses `msgpack <http://msgpack.org/>`_
- :class:`MsgPackBlosc` uses `msgpack <http://msgpack.org/>`_ and
  `Blosc <http://blosc.org/>`_

All codecs should implement the base class :class:`Codec`.

"""
__all__ = ['Codec', 'JSON', 'MsgPack', 'MsgPackBlosc']

import json
import sys

try:
    import blosc
except ImportError:
    blosc = None
try:
    import msgpack
except ImportError:
    msgpack = None


TYPESIZE = 8 if sys.maxsize > 2**32 else 4


class Codec:
    """Base class for all Codecs.

    Subclasses must implement :meth:`encode()` and :meth:`decode()`.

    """
    def __init__(self):
        self._serializers = {}
        self._deserializers = {}

    def __str__(self):
        return '%s[%s]' % (self.__class__.__name__,
                           ', '.join(s.__name__ for s in self._serializers))

    def encode(self, data):
        """Encode the given *data* and return a :class:`bytes` object."""
        raise NotImplementedError

    def decode(self, data):
        """Decode *data* from :class:`bytes` to the original data structure."""
        raise NotImplementedError

    def add_serializer(self, type, serialize, deserialize):
        """Add methods to *serialize* and *deserialize* objects typed *type*.

        This can be used to de-/encode objects that the codec otherwise
        couldn't encode.

        *serialize* will receive the unencoded object and needs to return
        an encodable serialization of it.

        *deserialize* will receive an objects representation and should return
        an instance of the original object.

        """
        typeid = len(self._serializers)
        self._serializers[type] = (typeid, serialize)
        self._deserializers[typeid] = deserialize

    def serialize_obj(self, obj):
        """Serialize *obj* to something that the codec can encode."""
        orig_type = otype = type(obj)
        if otype not in self._serializers:
            # Fallback to a generic serializer (if available)
            otype = object

        try:
            typeid, serialize = self._serializers[otype]
        except KeyError:
            raise TypeError('No serializer found for type "%s"' % orig_type) \
                from None

        return {'__type__': (typeid, serialize(obj))}

    def deserialize_obj(self, obj_repr):
        """Deserialize the original object from *obj_repr*."""
        # This method is called for *all* dicts so we have to check if it
        # contains a desrializable type.
        if '__type__' in obj_repr:
            typeid, data = obj_repr['__type__']
            obj_repr = self._deserializers[typeid](data)
        return obj_repr


class JSON(Codec):
    """A :class:`Codec` that uses *JSON* to encode and decode messages."""

    def encode(self, data):
        return json.dumps(data, default=self.serialize_obj).encode()

    def decode(self, data):
        return json.loads(data.decode(), object_hook=self.deserialize_obj)


class MsgPack(Codec):
    """A :class:`Codec` that uses *msgpack* to encode and decode messages."""
    def __init__(self):
        if msgpack is None:
            msg = ('Please install "msgpack-python" to use the %s codec: '
                   'pip install -U aiomas[MsgPack]' % self.__class__.__name__)
            raise ImportError(msg)
        super().__init__()

    def encode(self, data):
        return msgpack.packb(
            data, default=self.serialize_obj, use_bin_type=True)

    def decode(self, data):
        return msgpack.unpackb(data,
                               object_hook=self.deserialize_obj,
                               use_list=False,
                               encoding='utf-8')


class MsgPackBlosc(Codec):
    """A :class:`Codec` that uses *msgpack* to encode and decode messages and
    *blosc* to compress them."""
    def __init__(self):
        if msgpack is None or blosc is None:
            msg = ('Please install "msgpack-python" and "blosc" to use the %s '
                   'codec: pip install -U aiomas[MsgPackBlosc]' %
                   self.__class__.__name__)
            raise ImportError(msg)
        super().__init__()

    def encode(self, data):
        return blosc.compress(msgpack.packb(
            data, default=self.serialize_obj, use_bin_type=True), TYPESIZE)

    def decode(self, data):
        return msgpack.unpackb(blosc.decompress(bytes(data)),
                               object_hook=self.deserialize_obj,
                               use_list=False,
                               encoding='utf-8')
