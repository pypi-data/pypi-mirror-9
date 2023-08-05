"""
This module implements remote procedure calls (RPC) on top of request-reply
channels (see :mod:`aiomas.channel`).

RPC connections are represented by instances of :class:`RpcClient` (one for
each side of a :class:`aiomas.channel.Channel`).  They provide access to the
functions served by the remote side of the channel via :class:`Proxy`
instances.  Optionally, they can provide their own RPC service (via
:func:`rpc_service`) so that the remote side can make calls as well.

An RPC service is defined by a :class:`Router`.  A router resolves paths
requested by the remote side.  It can also handle sub-routers (which allows you
to build hierarchies for nested calls) and is able to perform a reverse-lookup
of a router (mapping a fuction to its path).

Routers provide the functions and methods of dictionaries or class instances.
Dict routers can be created by passing a dictionary to :class:`Router`.  For
classes, you create a :class:`Service` instance as `rpc` class attribute.  This
creates a *Descriptor* which then creates a new router instance for each class
instance.

Functions that should be callable from the remote side must be decorated with
:func:`expose()`; :func:`Router.expose()` and :func:`Service.expose()` are
aliases for it.

"""
__all__ = [
    'open_connection', 'start_server', 'expose',
    'Router', 'Service',
]

from asyncio import coroutine
import asyncio
import logging

import aiomas.channel
import aiomas.codecs


logger = logging.getLogger(__name__)


@coroutine
def open_connection(addr, *, router=None, add_to=None, **kwds):
    """Return an :class:`RpcClient` connected to *addr*.

    This is a convenience wrapper for :meth:`aiomas.channel.open_connection()`.
    All keyword arguments *(kwds)* are forwared to it.

    You can optionally pass a *router* to allow the remote site to call back
    to us.

    If you want to cleanly cancel all :func:`rpc_service()` tasks created for
    each connection made to *router*, you can pass a :class:`set` via *add_to*.
    All tasks will then be append to it.

    """
    if router is not None and type(router) is not Router:
        raise ValueError('"%s" is not a valid router.' % router)

    channel = yield from aiomas.channel.open_connection(addr, **kwds)
    return RpcClient(channel, router, add_to)


@coroutine
def start_server(addr, router, add_to=None, **kwds):
    """Start a server socket on *host:port* and create an RPC service with
    the provided *handler* for each new client.

    This is a convenience wrapper for :meth:`aiomas.channel.start_server()`.
    All keyword arguments *(kwds)* are forwared to it.

    *router* must be a :class:`Router` instance for the :func:`rpc_service()`
    that is started for each new connection.

    If you want to cleanly cancel all :func:`rpc_service()` tasks created for
    each connection made to *router*, you can pass a :class:`set` via *add_to*.
    All tasks will then be append to it.

    Raise a :exc:`ValueError` if *handler* is not decorated properly.

    """
    if type(router) is not Router:
        raise ValueError('"%s" is not a valid router.' % router)

    def fac(channel):
        return RpcClient(channel, router, add_to)

    server = yield from aiomas.channel.start_server(addr, fac, **kwds)
    return server


@coroutine
def rpc_service(router, channel):
    """Serve the functions provided by the :class:`Router` *router* via the
    :class:`~aiomas.channel.Channel` *channel*.

    Forward errors raised by the handler to the caller.

    Stop running when the connection closes.

    """
    loop = channel._loop

    try:
        while True:
            # Wait for a request
            request = yield from channel.recv()
            path, args, kwargs = request.content
            # logger.debug('Request: [%s, %s, %s]' % (path, args, kwargs))

            # Resolve requested path
            try:
                func = router.resolve(path)
            except LookupError as exc:
                yield from request.fail(exc)
                continue

            # Call requested function
            try:
                res = func(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    res = yield from loop.create_task(res)
            except Exception as e:
                yield from request.fail(e)  # pragma: no branch
            else:
                yield from request.reply(res)

    except (ConnectionError, asyncio.CancelledError):
        pass

    finally:
        channel.close()


def expose(func):
    """Decorator that enables RPC access to the decorated function.

    *func* will not be wrapped but only gain an ``__rpc__`` attribute.

    """
    if not hasattr(func, '__call__'):
        raise ValueError('"%s" is not callable.' % func)

    func.__rpc__ = True
    return func


class DictWrapper:
    """Wrapper for dicts so that they can be used as RPC routers."""
    __rpc__ = True

    def __init__(self, router, dict):
        self.dict = dict
        for key, val in dict.items():
            # Iterate over all entries and look for objects with routers.
            # Set *router* as parent to these sub-routers.
            if hasattr(val, 'rpc'):
                Router.set_sub_router(router, val.rpc, key)

        self.__getrpc__ = dict.__getitem__


class Router:
    """The Router resolves paths to functions provided by their object *obj*
    (or its children).  It can also perform a reverse lookup to get the path
    of the router (and the router's *obj*).

    The *obj* can be a class, an instance or a dict.

    """
    def __init__(self, obj):
        if type(obj) is not dict:
            # Mark *obj* as node in the RPC hierarchy and and create an alias
            # for accessing its child elements.
            obj.__rpc__ = True
            obj.__getrpc__ = obj.__getattribute__
        else:
            # We cannot set additional attributes to a dict, so we wrap it:
            obj = DictWrapper(self, obj)

        self.obj = obj  #: The object to which this router belongs to.
        self.name = ''  #: The name of the router (empty for root routers).
        self.parent = None  #: The parent router or ``None`` for root routers.

        self._cache = {}  # Maps already resolved paths to functions

    @property
    def path(self):
        """The path to this router (without trailing slash)."""
        router = self
        parts = []
        while router.parent is not None:
            parts.append(router.name)
            router = router.parent

        return '/'.join(parts)

    def resolve(self, path):
        """Resolve *path* and return the corresponding function.

        *path* is a string with path components separated by */* (without
        trailing slash).

        Raise a :exc:`LookupError` if no handler function can be found for
        *path* or if the function is not exposed (see :func:`expose()`).

        """
        try:
            obj = self._cache[path]
        except KeyError:
            obj = self.obj
            parts = path.split('/')
            for i, name in enumerate(parts):
                try:
                    obj = obj.__getrpc__(name)
                except (AttributeError, KeyError):
                    raise LookupError('Name "%s" not found in "%s"' %
                                      (name, '/'.join(parts[:i]))) from None

                if not hasattr(obj, '__rpc__'):
                    raise LookupError('"%s" is not exposed' % name)

            self._cache[path] = obj

        return obj

    expose = staticmethod(expose)
    """Alias for :func:`expose()`."""

    def add(self, name):
        """Add the sub-router *name* (stored at ``self.obj.<name>``) to this
        router.

        Convenience wrapper for :meth:`set_sub_router`.

        """
        router = getattr(self.obj, name).rpc
        self.set_sub_router(router, name)

    def set_sub_router(self, router, name):
        """Set *self* as parent for the *router* named *name*."""
        if type(router) is not Router:
            raise ValueError('"%s" is not a valid router.' % router)
        if router.parent is not None:
            raise ValueError('"%s" is already a sub router of "%s"' %
                             (router, router.parent))
        router.name = name
        router.parent = self


class Service:
    """A Data Descriptor that creates a new :class:`Router` instance for each
    class instance to which it is set.

    The attribute name for the Service should always be *rpc*::

        class Spam:
            rpc = aiomas.rpc.Service()

    You can optionally pass a list with the attribute names of classes with
    sub-routers.  This required to build hierarchies of routers, e.g.::

        class Eggs:
            rpc = aiomas.rpc.Service()


        class Spam:
            rpc = aiomas.rpc.Service(['eggs'])

            def __init__(self):
                self.eggs = Eggs()  # Instance with a sub-router

    """
    def __init__(self, sub_routers=()):
        self._sub_router_names = sub_routers

    def __set__(self, instance, value):
        """Raise :exc:`AttributeError` to forbid overwriting this attribute."""
        raise AttributeError('Read-only attribute.')

    def __get__(self, instance, cls):
        """If accessed from the class, return this Service instance.  If
        accessed from an *instance*, return the :class:`Router` instance for
        *instance*.

        """
        if instance is None:
            return self

        try:
            return instance.__dict__['rpc']
        except KeyError:
            router = instance.__dict__.setdefault('rpc', Router(instance))
            for name in self._sub_router_names:
                router.add(name)
            return router

    expose = staticmethod(expose)
    """Alias for :func:`expose()`."""


class RpcClient:
    """The RpcClient provides proxy objects for remote calls via its
    :attr:`remote` attribute.

    *channel* is a :class:`~aiomas.channel.Channel` instance for communicating
    with the remote side.

    If *router* is not ``None``, it will also start its own RPC service so the
    other side can make calls to us as well.

    If you want to cleanly cancel all :func:`rpc_service()` tasks created for
    each connection made to *router*, you can pass a :class:`set` via *add_to*.
    All tasks will then be append to it.

    """
    def __init__(self, channel, router=None, add_to=None):
        self.channel = channel
        self.channel.codec.add_serializer(object, self._serialize_obj,
                                          self._deserialize_obj)

        if router is not None:
            t = self.channel._loop.create_task(rpc_service(router, channel))
            if add_to is not None:  # pragma: no branch
                add_to.add(t)

    @property
    def remote(self):
        """A :class:`Proxy` for remote methods."""
        return Proxy(self.channel, '')

    def close(self):
        """Close the connection."""
        return self.channel.close()

    def _serialize_obj(self, obj):
        try:
            return obj.rpc.path
        except AttributeError:
            raise TypeError('"%s" does not provide an RPC service.' % obj)

    def _deserialize_obj(self, path):
        return Proxy(self.channel, path)


class Proxy:
    """Proxy object for remote objects and functions."""
    __slots__ = ('_channel', '_path')

    def __init__(self, channel, path):
        self._channel = channel
        self._path = path

    def __getattr__(self, name):
        """Return a new proxy for *name*."""
        path = name if not self._path else self._path + '/' + name
        return self.__class__(self._channel, path)

    def __call__(self, *args, **kwargs):
        """Call the remote method represented by this proxy and return its
        result.

        The result is a future, so you need to ``yield from`` it in order to
        get the actual return value (or exception).

        """
        if not self._path:
            raise AttributeError('No RPC function name specified.')
        return self._channel.send((self._path, args, kwargs))
