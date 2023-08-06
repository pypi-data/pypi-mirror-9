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
