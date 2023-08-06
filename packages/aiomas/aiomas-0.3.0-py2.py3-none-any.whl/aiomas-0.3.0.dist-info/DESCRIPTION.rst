aiomas – A library for multi-agent systems and RPC based on asyncio
===================================================================

*aiomas* is an easy-to-use library for *remote procedure calls (RPC)* and
*multi-agent systems (MAS)*. It’s written in pure Python on top of asyncio__.

Here is an example how you can write a simple multi-agent system:

.. code-block:: pycon

   >>> import asyncio
   >>> import aiomas
   >>>
   >>> class TestAgent(aiomas.Agent):
   ...     def __init__(self, container, name):
   ...         super().__init__(container, name)
   ...         print('Ohai, I am %s' % self.name)
   ...
   ...     @asyncio.coroutine
   ...     def run(self, addr):
   ...         remote_agent = yield from self.container.connect(addr)
   ...         ret = yield from remote_agent.service(42)
   ...         print('%s got %s from %s' % (self.name, ret, addr))
   ...
   ...     @aiomas.expose
   ...     def service(self, value):
   ...         return value
   >>>
   >>> loop = asyncio.get_event_loop()
   >>> c = aiomas.Container(('localhost', 5555))
   >>> agents = [c.spawn(TestAgent) for _ in range(2)]
   Ohai, I am agent://localhost:5555/0
   Ohai, I am agent://localhost:5555/1
   >>> loop.run_until_complete(agents[0].run('agent://localhost:5555/1'))
   agent://localhost:5555/0 got 42 from agent://localhost:5555/1
   >>> c.shutdown()

*aiomas* is released under the MIT license. It requires Python 3.4 and above
and runs on Linux, OS X, and Windows.

__ https://docs.python.org/3/library/asyncio.html


Installation
------------

*aiomas* requires Python >= 3.4.  It uses the *JSON* codec by default and only
has pure Python dependencies.

Install *aiomas* via pip__ by running:

.. code-block:: bash

   $ pip install aiomas

You can enable the optional MsgPack__ codec or its Blosc__ compressed version
by installing the corresponding features (note, that you need a C compiler to
install them):

.. code-block:: bash

   $ pip install aiomas[MsgPack]       # Enables the MsgPack codec
   $ pip install aiomas[MsgPackBlock]  # Enables the MsgPack and MsgPackBlosc codecs

__ https://pip.pypa.io/
__ https://pypi.python.org/pypi/msgpack-python/
__ https://pypi.python.org/pypi/blosc/


Features
--------

*aiomas* just puts three layers of abstraction around raw TCP / unix domain
sockets provided by *asyncio*:

Agents and agent containers:
  The top-layer provides a simple base class for your own agents. All agents
  live in a container.

  Containers take care of creating agents and performing the communication
  between them.

  The container provides a *clock* for the agents. This clock can either be
  synchronized with the real (wall-clock) time or be set by an external process
  (e.g., other simulators).

RPC:
  The *rpc* layer implements remote procedure calls which let you call methods
  on remote objects nearly as if they were normal objects:

  Instead of ``ret = obj.meth(arg)`` you write ``ret = yield from
  obj.meth(arg)``.

Request-reply channel:
  The *channel* layer is the basis for the *rpc* layer. It sends JSON__ or
  MsgPack__ encoded byte strings over TCP or unix domain sockets. It also maps
  replies (of success or failure) to their corresponding request.

Although you usually want to use the *agent* layer, it is perfectly okay to
only use the *rpc* or *channel* layer.

__ http://www.json.org/
__ http://msgpack.org/


Planned features
^^^^^^^^^^^^^^^^

Some ideas for future releases:

- SSL/TLS support for TCP sockets

- Optional automatic re-connect after connection loss

- Helper for binding a socket to a random free port


Contribute
----------

- Issue Tracker: https://bitbucket.org/ssc/aiomas/issues?status=new&status=open
- Source Code: https://bitbucket.org/ssc/aiomas/src

Set-up a development environment with:

.. code-block:: bash

   $ virtualenv -p `which python3` aiomas
   $ pip install -r requirements.txt

Run the tests with:

.. code-block:: bash

   $ py.test
   $ # or
   $ tox


Support
-------

- Documentation: http://aiomas.readthedocs.org/en/latest/

- Mailing list: we don’t have one, yet.  Meanwhile, you can use `Stack
  Overflow <http://stackoverflow.com/questions/tagged/aiomas>`_.


License
-------

The project is licensed under the MIT license.


Changelog
=========

0.3.0 – 2015-03-11
------------------

- [CHANGE] Removed LocalProxies and everything related to it because they
  caused several problems.  That means that agents within a single container
  now also communicate via TCP sockets.  Maybe something similar but more
  robust will be reintroduced in a later release.

- [CHANGE] ``Channel.send()`` is no longer a coroutine.  It returns a Future
  instead.

- [CHANGE] Removed ``Container.get_url_for()`` which didn’t (and couldn’t) work
  as I originally assumed.

- [CHANGE] ``JSON`` is now the default codec.  msgpack and blosc don’t get
  installed by default.  This way, we only have pure Python dependencies for
  the default installation which is very handy if you are on Windows.  You can
  enable the other codecs via ``pip install -U aiomas[MsgPack]`` or ``pip
  install -U aiomas[MsgPackBlosc]``.

- [NEW] Support for Python 3.4.0 and 3.4.1 (yes, Python 3.3 with asyncio works,
  too, but I’ll drop support for it as soon as it becomes a burden) (Resolves
  `issue #6`_).

- [NEW] ``ExternalClock`` accepts a date string or an Arrow object to set the
  inital date and time.

- [NEW] ``aiomas.util.async()`` which is like ``asyncio.async()`` but registers
  a callback that instantly captures and raises exceptions, instead of delaying
  them until the task gets garbage collected.

- [NEW] The agent container adds a serializer for Arrow dates.

- [NEW] ``Proxy`` implements ``__eq__()`` and ``__hash__()``.  Two different
  proxy objects sharing the same channel and pointing to the same remote
  function will no appear to be equal.  This makes it less error prone to use
  Proxy instances as keys in dictionaries.

- [NEW] Updated and improved flow-control for ``Channel`` and its protocol.

- [NEW] Improved error handling if the future returned by ``Channel.send()``
  is triggered or cancelled by an external party (e.g., by going out of scope).
  If asyncio’s DEBUG mode is enabled, you will even get more detailed error
  messages.

- [NEW] ``MessagePackBlosc`` codec.  It uses msgpack to serialize messages and
  blosc to compress them.  It can massively reduce the message size and
  consumes very little CPU time.

- [NEW] A Contract Net example
  (https://bitbucket.org/ssc/aiomas/src/tip/examples/contractnet.py)

- [NEW] ``__str__()`` representations for agents, containers and codecs (fixes
  `issue #5`_).

- [FIX] `issue #7`_: Improved error handling and messages if the
  (de)serialization raises an exception.

- [FIX] Containers now work with unix domain sockets.

- [FIX] Various minor bug-fixes

.. _`issue #5`: https://bitbucket.org/ssc/aiomas/issue/5/
.. _`issue #6`: https://bitbucket.org/ssc/aiomas/issue/6/
.. _`issue #7`: https://bitbucket.org/ssc/aiomas/issue/7/


0.2.0 - 2015-01-23
------------------

- [CHANGE] The *MsgPack* codec is now the default.  Thus, *msgpack-python* is
  now a mandatory dependency.

- [CHANGE] Renamed ``RpcClient.call`` to ``RpcClient.remote``.

- [NEW] ``aiomas.agent`` module with an ``Agent`` base class and
  a ``Container`` for agents.  Agents within a container communicate via direct
  method calls.  Agents in different containers use RPC.

- [NEW] ``aiomas.clock`` module which offers various clocks for a MAS:

  - ``AsyncioClock`` is a real-time clock and wraps asyncio's ``time()``,
    ``sleep()``, ``call_later()`` and ``call_at()`` functions.

  - ``ExternalClock`` can be synchronized with external simulation
    environments.  This allows you to *stop* the time or let it pass
    faster/slower than the wall-clock time.

- [NEW] Support for unix domain sockets in ``aiomas.channel`` and
  ``aiomas.rpc``.

- [NEW] "rpc_service()" tasks created by an RPC server can now be collected
  so that you can wait for their completion before you shutdown your program.

- [NEW] Added contents to the README and created a Sphinx project.  Only the
  API reference is done yet.  A tutorial and topical guides will follow.

- [FIX] aiomas with the JSON codec is now compatible to simpy.io



0.1.0 – 2014-12-18
------------------

Initial release with the following features:

- A *request-reply channel* via TCP that allows to send multiple messages and
  to asynconously wait for results (or an exception).

- Messages can be serialized with *JSON* or *msgpack*.

- The underlying communication protocol should be compatible with `simpy.io
  <https://bitbucket.org/simpy/simpy.io/>`_ (if you use JSON and no custom
  serializers).

- Remote procedure calls (RPCs) supporting nested handlers and bidirectional
  calls (callees can make calls to the caller before returning the actual
  result).


Authors
=======

The original author of aiomas is Stefan Scherfke.

The development is kindly supported by `OFFIS <www.offis.de/en/>`_.


