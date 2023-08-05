aiomas – A library for multi-agent systems and RPC based on asyncio
===================================================================

*aiomas* is an easy-to-use library for *remote procedure calls (RPC)* and
*multi-agent systems (MAS)*. It’s written in pure Python on top of asyncio__.

Here is an example how you can write a simple multi-agent system:

.. code-block:: python

   >>> import asyncio
   >>> import aiomas
   >>>
   >>> class TestAgent(aiomas.Agent):
   ...     def __init__(self, container, name):
   ...         super().__init__(container, name)
   ...         print('Ohai, I’m %s' % self.name)
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
   >>> agents = [c.spawn(TestAgent) for i in range(2)]
   Ohai, I’m agent://localhost:5555/0
   Ohai, I’m agent://localhost:5555/1
   >>> loop.run_until_complete(agents[0].run('agent://localhost:5555/1'))
   agent://localhost:5555/0 got 42 from agent://localhost:5555/1
   >>> c.shutdown()

*aiomas* is released under the MIT license. It requires Python 3.4 and above
and runs on Linux, OS X, and Windows.

__ https://docs.python.org/3/library/asyncio.html


Features
--------

*aiomas* just puts three layers of abstraction around raw TCP / unix domain
sockets provided by *asyncio*:

Agents and agent containers:
  The top-layer provides a simple base class for your own agents. All agents
  live in a container.

  Containers take care of creating agents and performing the communication
  between them. Only agents in different containers talk via network sockets.
  Agents within the same container use direct method calls.

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


Installation
------------

*aiomas* requires Python >= 3.4 and msgpack-python__ (it may also run on
Python 3.3 with the asyncio__ package, but this is untested).

Install *aiomas* via pip__ by running:

.. code-block:: bash

   $ pip install aiomas

__ https://pypi.python.org/pypi/msgpack-python
__ https://pypi.python.org/pypi/asyncio
__ https://pip.pypa.io/


Contribute
----------

- Issue Tracker:
- Source Code:

Set-up a development environment with:

.. code-block:: bash

   $ pip install -r requirements.txt

Run the tests with:

.. code-block:: bash

   $ py.test


Support
-------

- Documentation:
- Mailing list:


License
-------

The project is licensed under the MIT license.


Changelog
=========

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

- [NEW] "rpc_service()" tasks created by an RPC server can now be collected
  so that you can wait for their completion before you shutdown your program.

- [NEW] Added contents to the README and created a Sphinx project.  Only the
  API reference is done yet.  A tutorial and topical guides will follow.

- [FIX] aiomas with the JSON codec is now compatible to simpy.io



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


