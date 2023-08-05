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
