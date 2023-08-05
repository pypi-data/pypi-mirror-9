asyncio integration with ZeroMQ
===============================

asyncio (PEP 3156) support for ZeroMQ.

.. image:: https://travis-ci.org/aio-libs/aiozmq.svg?branch=master
   :target: https://travis-ci.org/aio-libs/aiozmq

Documentation
-------------

See http://aiozmq.readthedocs.org

Simple high-level client-server RPC example::

    import asyncio
    import aiozmq.rpc


    class ServerHandler(aiozmq.rpc.AttrHandler):

        @aiozmq.rpc.method
        def remote_func(self, a:int, b:int) -> int:
            return a + b


    @asyncio.coroutine
    def go():
        server = yield from aiozmq.rpc.serve_rpc(
            ServerHandler(), bind='tcp://127.0.0.1:5555')
        client = yield from aiozmq.rpc.connect_rpc(
            connect='tcp://127.0.0.1:5555')

        ret = yield from client.call.remote_func(1, 2)
        assert 3 == ret

        server.close()
        client.close()

    asyncio.get_event_loop().run_until_complete(go())

Low-level request-reply example::

    import asyncio
    import aiozmq
    import zmq

    @asyncio.coroutine
    def go():
        router = yield from aiozmq.create_zmq_stream(
            zmq.ROUTER,
            bind='tcp://127.0.0.1:*')

        addr = list(router.transport.bindings())[0]
        dealer = yield from aiozmq.create_zmq_stream(
            zmq.DEALER,
            connect=addr)

        for i in range(10):
            msg = (b'data', b'ask', str(i).encode('utf-8'))
            dealer.write(msg)
            data = yield from router.read()
            router.write(data)
            answer = yield from dealer.read()
            print(answer)
        dealer.close()
        router.close()

    asyncio.get_event_loop().run_until_complete(go())


Requirements
------------

* Python_ 3.3+
* pyzmq_ 13.1+
* asyncio_ or Python 3.4+
* optional submodule ``aiozmq.rpc`` requires msgpack-python_ 0.4+



License
-------

aiozmq is offered under the BSD license.

.. _python: https://www.python.org/
.. _pyzmq: https://pypi.python.org/pypi/pyzmq
.. _asyncio: https://pypi.python.org/pypi/asyncio
.. _msgpack-python: https://pypi.python.org/pypi/msgpack-python

CHANGES
-------

0.6.0 (XXXX-XX-XX)
^^^^^^^^^^^^^^^^^^

* Process asyncio specific exceptions as builtins.

* Add repr(exception) to rpc server call logs if any

* Add transport.get_write_buffer_limits() method

* Add __repr__ to transport

* Add zmq_type to tr.get_extra_info()

* Add zmq streams

0.5.2 (2014-10-09)
^^^^^^^^^^^^^^^^^^

* Poll events after sending zmq message for eventless transport

0.5.1 (2014-09-27)
^^^^^^^^^^^^^^^^^^

* Fix loopless transport implementation.

0.5.0 (2014-08-23)
^^^^^^^^^^^^^^^^^^

* Support zmq devices in aiozmq.rpc.serve_rpc()

* Add loopless 0MQ transport

0.4.1 (2014-07-03)
^^^^^^^^^^^^^^^^^^

* Add exclude_log_exceptions parameter to rpc servers.

0.4.0 (2014-05-28)
^^^^^^^^^^^^^^^^^^

* Implement pause_reading/resume_reading methods in ZmqTransport.

0.3.0 (2014-05-17)
^^^^^^^^^^^^^^^^^^

* Add limited support for Windows.

* Fix unstable test execution, change ZmqEventLoop to use global
  shared zmq.Context by default.

* Process cancellation on rpc servers and clients.

0.2.0 (2014-04-18)
^^^^^^^^^^^^^^^^^^

* msg in msg_received now is a list, not tuple

* Allow to send empty msg by trsansport.write()

* Add benchmarks

* Derive ServiceClosedError from aiozmq.rpc.Error, not Exception

* Implement logging from remote calls at server side (log_exceptions parameter).

* Optimize byte counting in ZmqTransport.

0.1.3 (2014-04-10)
^^^^^^^^^^^^^^^^^^

* Function default values are not passed to an annotaion.
  Add check for libzmq version (should be >= 3.0)

0.1.2 (2014-04-01)
^^^^^^^^^^^^^^^^^^

* Function default values are not passed to an annotaion.

0.1.1 (2014-03-31)
^^^^^^^^^^^^^^^^^^

* Rename plural module names to single ones.

0.1.0 (2014-03-30)
^^^^^^^^^^^^^^^^^^

* Implement ZmqEventLoop with *create_zmq_connection* method which operates
  on zmq transport and protocol.

* Implement ZmqEventLoopPolicy.

* Introduce ZmqTransport and ZmqProtocol.

* Implement zmq.rpc with RPC, PUSHPULL and PUBSUB protocols.

