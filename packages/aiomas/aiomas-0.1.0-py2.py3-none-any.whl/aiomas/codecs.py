"""
This package imports the codecs that can be used for de- and encoding incoming
and outgoing messages:

- :class:`JSON` uses `JSON <http://www.json.org/>`_
- :class:`MsgPack` uses `msgpack <http://msgpack.org/>`_

All codecs should implement the base class :class:`Codec`.

"""
import json

try:
    import msgpack
except ImportError:
    msgpack = None


class Codec:
    """Base class for all Codecs.

    Subclasses must implement :meth:`encode()` and :meth:`decode()`.

    """
    def __init__(self):
        self._serializers = {}
        self._deserializers = {}

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
        otype = type(obj)
        if otype not in self._serializers:
            # Fallback to a generic serializer (if available)
            otype = object

        try:
            typeid, serialize = self._serializers[otype]
        except KeyError:
            raise TypeError('No serializer found for type "%s"' % otype) \
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
    """Uses *JSON* to encode and decode messages."""
    def encode(self, data):
        return json.dumps(data, default=self.serialize_obj).encode()

    def decode(self, data):
        return json.loads(data.decode(), object_hook=self.deserialize_obj)


class MsgPack(Codec):
    """Uses *msgpack* to encode and decode messages."""
    def __init__(self):
        if msgpack is None:
            raise ImportError('Please install "msgpack-pyhton" in order to '
                              'use the MsgPack codec.')
        super().__init__()

    def encode(self, data):
        return msgpack.packb(data, default=self.serialize_obj)

    def decode(self, data):
        return msgpack.unpackb(data, object_hook=self.deserialize_obj,
                               use_list=False, encoding='utf-8')
