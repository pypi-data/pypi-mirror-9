"""
This module implements the base class for agents (:class:`Agent`) and
containers for agents (:class:`Container`).

Every agent must live in a container.  A container can contain one ore more
agents.  Containers are responsible for making connections to other containers
and agents.  They also provide a factory function for spawning new agent
instances and registering them with the container.

Thus, the :class:`Agent` base class is very light-weight.  It only has a name,
a reference to its container and an RPC router (see :mod:`aiomas.rpc`).

"""
__all__ = ['Container', 'Agent', 'LocalProxy']

import asyncio
import traceback
import socket

from aiomas.exceptions import RemoteException
import aiomas.codecs
import aiomas.clocks
import aiomas.rpc


AGENT_PROTOCOL = 'agent://'
AGENT_PROTOCOL_LEN = len(AGENT_PROTOCOL)
AGENT_URL = AGENT_PROTOCOL + '{host}:{port}/{aid}'


class Container:
    """Container for agents.

    It can instantiate new agents via :meth:`spawn()` and can create
    connections to other agents (via :meth:`connect()`).

    In order to destroy a container and close all of its sockets, call
    :meth:`shutdown()`.

    When a container is created, it also creates a server socket and binds it
    to *addr* which is a ``('host', port)`` tuple (see the *host* and *port*
    parameters of :meth:`asyncio.BaseEventLoop.create_server()` for details).

    You can optionally also pass a *codec* instance
    (:class:`~aiomas.codecs.JSON` or :class:`~aiomas.codecs.MsgPack`
    (default)). Containers can only "talk" to containers using the same codec.

    To decouple a multi-agent system from the system clock, you can pass an
    optional *clock* object which should be an instance of
    :class:`~aiomas.clocks.BaseClock`.  This makes it easier to integrate your
    system with other simulators that may provide a clock for you or to let
    your MAS run as fast as possible.  By default,
    :class:`~aiomas.clocks.AsyncioClock` will be used.

    """
    def __init__(self, addr, codec=None, clock=None):
        if codec is None:
            codec = aiomas.codecs.MsgPack()
        if clock is None:
            clock = aiomas.clocks.AsyncioClock()

        self._addr = addr
        self._codec = codec
        self._clock = clock
        self.clock = clock

        # Set a sensbile hostname
        if addr[0] in [None, '', '::', '0.0.0.0']:
            # Use the fully qualified domain name if we bind to all interface
            self._host = socket.getfqdn()
        else:
            # Use the IP address or host name if not
            self._host = addr[0]
        self._port = addr[1]

        # The agents managed by this container.
        # The agents' routers are subrouters of the container's root router.
        self._agents = {}
        self._router = aiomas.rpc.Router(self._agents)

        # RPC service for this container
        self._tcp_server = None
        self._tcp_services = set()
        self._start_tcp_server = asyncio.async(self._start_tcp_server())

        # Caches
        self._local_addresses = set()  # Addresses that point to "self"
        self._tcp_connections = {}  # RPC cons. to remote containers by addr.

    @asyncio.coroutine
    def _start_tcp_server(self):
        """Helper task to create an RPC server for this container."""
        self._tcp_server = yield from aiomas.rpc.start_server(
            self._addr,
            self._router,
            codec=self._codec,
            add_to=self._tcp_services)

    def spawn(self, agent_type, *args, **kwargs):
        """Create an instance of *agent_type*, passing a reference to this
        container, a name and the provided *args* and **kwargs** to it.

        This is equivalent to ``agent = agent_type(container, name, *args,
        **kwargs)``, but also registers the agent with the container.

        """
        aid = str(len(self._agents))
        url = AGENT_URL.format(host=self._host, port=self._port, aid=aid)
        agent = agent_type(self, url, *args, **kwargs)
        agent.rpc  # Initialize router (sets the "__rpc__" attribute to agent)
        self._agents[aid] = agent
        return agent

    @asyncio.coroutine
    def connect(self, url):
        """Connect to the argent available at *url* and return a proxy to it.

        *url* is a string ``agent://<host>:<port>/<agent-name>``.

        If the remote agent belongs to a different container than the
        connecting agent, return a :class:`aiomas.rpc.Proxy` (which performs
        remote procedure calls via TCP sockets).  If the remote agent lives in
        the same containers as the connecting agent, return
        a :class:`LocalProxy` (which uses direct method calls and no
        networking).  Both proxy types have the same behavior and raise
        a :exc:`~aiomas.exceptions.RemoteException` if an exception is raised
        in the remote methods.

        """
        # We only want *real* RPC for agents in remote containers. Agents in
        # the local container should use normal method calls instead.
        #
        # Finding out whether "host:port" refers to the local container is
        # surprisingly hard, especially when the container's server socket is
        # bound to "None", "::", or "0.0.0.0". Our algorithm works as follows:
        #
        # 1. If "addr" is known to be this container, return a LocalProxy
        #
        # 2. If not, check if we already have a connection to "addr".
        #
        #    a) If so, we know it must be remote. Return a Proxy
        #
        #    b) If there is no connection yet, we don't know whether it's local
        #       or remote. Go to 3.
        #
        # 3. Make a connection to "addr".
        #
        #    a) If the peer port is equal to the port our container is bound to
        #       and if the peer host is the same as the host our local socket
        #       uses, it must be a connection to the local container.
        #
        #       Close the connection, remember "addr" to be local and
        #       return a LocalProxy.
        #
        #    b) Else, it must be a connection to a remote container. Cache it
        #       and return a Proxy.
        #
        # /tests/test_agent.py contains some examples for this.

        addr, agent_id = self._parse_url(url)

        if addr in self._local_addresses:
            # Local agent
            return self._make_local_proxy(agent_id)
        elif addr in self._tcp_connections:
            # Remote agent
            rpc_con = self._tcp_connections[addr]
            return getattr(rpc_con.remote, agent_id)
        else:
            # We don't know yet
            rpc_con = yield from aiomas.rpc.open_connection(
                addr,
                router=self._router,
                add_to=self._tcp_services,
                codec=self._codec)

            peerhost = rpc_con.channel.get_extra_info('peername')[0]
            sockhost = rpc_con.channel.get_extra_info('sockname')[0]
            peerport = addr[1]
            if peerport == self._port and peerhost == sockhost:
                # Okay, must be a local agent. Remember this!
                self._local_addresses.add(addr)
                rpc_con.close()
                return self._make_local_proxy(agent_id)
            else:
                # Okay, it's a remote agent. Cache the connection.
                self._tcp_connections[addr] = rpc_con
                return getattr(rpc_con.remote, agent_id)

    def shutdown(self, async=False):
        """Close the container's server socket and the RPC services for all
        outgoing TCP connections.

        If *async* is left to ``False``, this method calls
        :meth:`asyncio.BaseEventLoop.run_until_complete()` in order to wait
        until all sockets are closed.

        If the event loop is already running when you call this method, set
        *async* to ``True``. The return value then is a coroutine that you need
        to ``yield from`` in order to actually shut the container down::

            yield from container.shutdown(async=True)

        """
        @asyncio.coroutine
        def _shutdown():
            # Wait until the TCP server is up before trying to terminate it.
            # self._tcp_server is None until this task is finished!
            yield from self._start_tcp_server
            if self._tcp_server:

                # Request closing the server socket and cancel the services
                self._tcp_server.close()
                for service in self._tcp_services:
                    service.cancel()

                # Close all outgoing connections
                for con in self._tcp_connections.values():
                    con.close()

                # Wait for server and services to actually terminate
                yield from asyncio.gather(self._tcp_server.wait_closed(),
                                          *self._tcp_services)

                self._tcp_server = None
                self._tcp_services = None

        if async:
            return _shutdown()
        else:
            asyncio.get_event_loop().run_until_complete(_shutdown())

    def _parse_url(self, url):
        """Parse the agent *url* and return a ``((host, port), agent)`` tuple.

        Raise a :exc:`ValueError` if the URL cannot be parsed.

        """
        if url[:AGENT_PROTOCOL_LEN] != AGENT_PROTOCOL:
            raise ValueError('Agent URL must be preceded by "agent://"')

        try:
            addr, agent_id = url[AGENT_PROTOCOL_LEN:].split('/', 1)

            host, port = addr.rsplit(':', 1)
            if host[0] == '[' and host[-1] == ']':
                # Looks like we got an IPv6 address ("[host]:port")
                host = host[1:-1]
            port = int(port)
        except (IndexError, ValueError):
            raise ValueError('Cannot parse agent URL "%s"' % url) from None

        return (host, port), agent_id

    def _make_local_proxy(self, agent_id):
        """Helper for creating a :class:`LocalProxy` instance."""
        try:
            return LocalProxy(self._agents[agent_id], '')
        except KeyError:
            raise ValueError('Local agent "%s" does not exist' % agent_id)


class Agent:
    """Base class for all agents."""

    rpc = aiomas.rpc.Service()
    """Descriptor that creates an RPC :class:`~aiomas.rpc.Router` for every
    agent instance.

    You can override this in a sub-class if you need to.  (Usually, you don't.)

    """

    def __init__(self, container, name):
        self.__container = container
        self.__name = name

    @property
    def container(self):
        """The :class:`Container` that the agent lives in."""
        return self.__container

    @property
    def name(self):
        """The agent's name. It is formatted like an agent URL and can
        usually (but not necessarily) be used to connect to this agent."""
        return self.__name


class LocalProxy:
    """Proxy for local objects and functions.

    It has the same interface as the actual :class:`~aiomas.rpc.Proxy` but
    directly calls the proxied methods instead of sending messages over the
    network.

    """
    # This class mimics rpc.Proxy but instead of sending messages via the
    # network it has a reference to an actual, local object and does normal
    # method calls on it.
    #
    # To be exchangeable with a Proxy, it has to behave similarly, that is:
    #
    # - Attribute access via __getattr__() must also return a LocalProxy and
    #   may not raise an AttributeError if an attribute does not exists in the
    #   wrapped object.
    #
    # - __call__() must be a coroutine or return a Future so that the user can
    #   "yield from" it. Any errors raised during path resolution or calling
    #   the wrapped function must be wrapped with a RemoteException.

    __slots__ = ('_obj', '_path')

    def __init__(self, obj, path):
        self._obj = obj
        self._path = path

    def __getattr__(self, name):
        """Return a new proxy for *name*."""
        path = name if not self._path else self._path + '/' + name
        return self.__class__(self._obj, path)

    def __call__(self, *args, **kwargs):
        """Call the remote method represented by this proxy and return its
        result.

        This method is a coroutine so you need to ``yield from`` it in order to
        get the actual return value (or exception).

        """
        # This method uses code (copied from or similar to):
        #
        # - rpc.rpc_service(): path resolution and execution of the
        #   corresponding function.
        #
        # - channel.Request.fail(), channel.Channel._feed_data(): Wrapping an
        #   exception with a RemoteException.
        if not self._path:
            raise AttributeError('No RPC function name specified.')

        @asyncio.coroutine
        def do_call():
            # Resolve requested path
            try:
                func = self._obj.rpc.resolve(self._path)
            except LookupError as exc:
                raise self._make_remote_exception(exc)

            # Call requested function
            try:
                res = func(*args, **kwargs)
                if asyncio.iscoroutine(res):
                    res = yield from asyncio.async(res)
            except Exception as exc:
                raise self._make_remote_exception(exc)

            return res

        return do_call()

    def _make_remote_exception(self, exception):
        """Helper to create a :exc:`aiomas.exceptions.RemoteException`."""
        stacktrace = traceback.format_exception(
            exception.__class__, exception, exception.__traceback__)
        origin = self._obj.name
        return RemoteException(origin, ''.join(stacktrace))
