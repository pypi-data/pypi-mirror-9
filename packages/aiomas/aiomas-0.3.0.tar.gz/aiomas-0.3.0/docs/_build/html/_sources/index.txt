==================================
Welcome to aiomas's documentation!
==================================

`PyPI <https://pypi.python.org/pypi/aiomas>`_ |
`Source <https://bitbucket.org/ssc/aiomas/source>`_ |
`Issues <https://bitbucket.org/ssc/aiomas/issues>`_ |
`Mailing list <...>`_

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


Contents:
=========

.. toctree::
   :maxdepth: 2

   overview
   agent
   rpc
   channel
   codecs
   api_reference/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
