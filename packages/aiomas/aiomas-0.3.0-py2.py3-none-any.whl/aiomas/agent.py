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
__all__ = ['Container', 'Agent']

import asyncio
import re
import socket

import aiomas.channel
import aiomas.codecs
import aiomas.clocks
import aiomas.rpc


AGENT_PROTOCOL = 'agent://'
AGENT_PROTOCOL_LEN = len(AGENT_PROTOCOL)
AGENT_TCP_URL = AGENT_PROTOCOL + '{host}:{port}/{aid}'
AGENT_UNIX_URL = AGENT_PROTOCOL + '[{path}]/{aid}'

# Valid urls:
# - hostname:port/aid
# - ipv4:port/aid
# - [ipv6]:port/aid
# - [path]/aid
# regex: (ipv6_or_path|ipv4_or_hostname)/aid
RE_AGENT_URL = re.compile(r'(\[(?P<ipv6_or_path>.+?)\](:(?P<ipv6_port>\d+))?|'
                          r'(?P<host>.+?):(?P<port>\d+))'
                          r'/(?P<aid>.+)')


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
            codec = aiomas.channel.DEFAULT_CODEC()
        if clock is None:
            clock = aiomas.clocks.AsyncioClock()

        self._addr = addr
        self._codec = codec
        self._clock = clock

        codec.add_serializer(*aiomas.clocks.arrow_serializer())

        # Set a sensbile hostname
        if type(addr) is tuple:
            if addr[0] in [None, '', '::', '0.0.0.0']:
                # Use the FQDN if we bind to all interfaces
                self._host = socket.getfqdn()
            else:
                # Use the IP address or host name if not
                self._host = addr[0]
            self._port = addr[1]
        else:
            self._host = None
            self._port = None

        # The agents managed by this container.
        # The agents' routers are subrouters of the container's root router.
        self._agents = {}
        self._router = aiomas.rpc.Router(self._agents)

        # RPC service for this container
        self._tcp_server = None
        self._tcp_services = set()
        self._tcp_server_started = asyncio.async(self._start_tcp_server())
        self._tcp_server_started.add_done_callback(lambda fut: fut.result())

        # Caches
        self._connections = {}  # RPC cons. to containers by addr.

    def __str__(self):
        return '%s(%r, %s, %s)' % (self.__class__.__name__, self._addr,
                                   self._codec, self._clock.__class__.__name__)

    @property
    def codec(self):
        """The codec used by this container.  Instance of
        :class:`aiomas.codecs.Codec`."""
        return self._codec

    @property
    def clock(self):
        """The clock of the container.  Instance of
        :class:`aiomas.clocks.BaseClock`."""
        return self._clock

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
        if self._host is None:
            url = AGENT_UNIX_URL.format(path=self._addr, aid=aid)
        else:
            url = AGENT_TCP_URL.format(host=self._host, port=self._port,
                                       aid=aid)
        agent = agent_type(self, url, *args, **kwargs)
        agent.rpc  # Initialize router (sets the "__rpc__" attribute to agent)
        self._agents[aid] = agent
        self._router.set_sub_router(agent.rpc, aid)
        return agent

    @asyncio.coroutine
    def connect(self, url):
        """Connect to the argent available at *url* and return a proxy to it.

        *url* is a string ``agent://<host>:<port>/<agent-name>``.

        """
        addr, agent_id = self._parse_url(url)

        if addr in self._connections:
            rpc_con = self._connections[addr]
        else:
            rpc_con = yield from aiomas.rpc.open_connection(
                addr,
                router=self._router,
                add_to=self._tcp_services,
                codec=self._codec)
            self._connections[addr] = rpc_con

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
            yield from self._tcp_server_started

            if self._tcp_server:

                # Request closing the server socket and cancel the services
                self._tcp_server.close()
                for service in self._tcp_services:
                    service.cancel()

                # Close all outgoing connections
                for con in self._connections.values():
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

        url = url[AGENT_PROTOCOL_LEN:]

        match = RE_AGENT_URL.match(url)
        if match is None:
            raise ValueError('Cannot parse agent URL "%s"' % url)

        ipv6_or_path, ipv6_port = match.group('ipv6_or_path', 'ipv6_port')
        host, port = match.group('host', 'port')
        aid = match.group('aid')

        if ipv6_or_path and ipv6_port is None:
            # We got a unix domain socket path
            addr = ipv6_or_path

        elif ipv6_or_path and ipv6_port:
            # We got an IPv6 address and a port
            assert (host, port) == (None, None)
            addr = (ipv6_or_path, int(ipv6_port))

        else:
            # We got a hostname or IPv4 address and a port
            assert host is not None
            assert port is not None
            addr = (host, int(port))

        return addr, aid


class Agent:
    """Base class for all agents."""

    rpc = aiomas.rpc.Service()
    """Descriptor that creates an RPC :class:`~aiomas.rpc.Router` for every
    agent instance.

    You can override this in a sub-class if you need to.  (Usually, you don't.)

    """
    def __init__(self, container, name):
        if type(container) != Container:
            raise TypeError('"container" must be a "Container" instance but '
                            'is %s' % container)
        if type(name) != str or not name.startswith(AGENT_PROTOCOL):
            raise TypeError('"name" must be an agent URL but is %s' % name)

        self.__container = container
        self.__name = name

    def __str__(self):
        return self.__name

    @property
    def container(self):
        """The :class:`Container` that the agent lives in."""
        return self.__container

    @property
    def name(self):
        """The agent's name. It is formatted like an agent URL and can
        usually (but not necessarily) be used to connect to this agent."""
        return self.__name
