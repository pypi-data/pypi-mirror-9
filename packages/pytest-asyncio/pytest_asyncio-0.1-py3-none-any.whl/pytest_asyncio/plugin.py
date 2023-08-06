import asyncio
from concurrent.futures import ProcessPoolExecutor
from contextlib import closing
import inspect
import socket
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers",
                            "asyncio: "
                            "mark the test as a coroutine, it will be "
                            "run using an asyncio event loop")
    config.addinivalue_line("markers",
                            "asyncio_process_pool: "
                            "mark the test as a coroutine, it will be "
                            "run using an asyncio event loop with a process "
                            "pool")


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and inspect.isgeneratorfunction(obj):
        item = pytest.Function(name, parent=collector)
        if 'asyncio' in item.keywords or 'asyncio_process_pool' in item.keywords:
            return list(collector._genfunctions(name, obj))


def _argnames(func):
    spec = inspect.getfullargspec(func)
    if spec.defaults:
        return spec.args[:-len(spec.defaults)]
    return spec.args


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """A hook wrapper."""
    if 'asyncio_process_pool' in pyfuncitem.keywords:
        event_loop = pyfuncitem.funcargs.get('event_loop_process_pool')
        funcargs = dict((arg, pyfuncitem.funcargs[arg])
                        for arg in _argnames(pyfuncitem.obj))
        event_loop.run_until_complete(asyncio.async(pyfuncitem.obj(**funcargs)))
        # prevent other pyfunc calls from executing
        return True
    elif 'asyncio' in pyfuncitem.keywords:
        event_loop = pyfuncitem.funcargs.get('event_loop')
        funcargs = dict((arg, pyfuncitem.funcargs[arg])
                        for arg in _argnames(pyfuncitem.obj))
        event_loop.run_until_complete(asyncio.async(pyfuncitem.obj(**funcargs)))
        # prevent other pyfunc calls from executing
        return True


def pytest_runtest_setup(item):
    if 'asyncio' in item.keywords and 'event_loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('event_loop')

    if ('asyncio_process_pool' in item.keywords and
                'event_loop_process_pool' not in item.fixturenames):
        item.fixturenames.append('event_loop_process_pool')


@pytest.fixture
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()

    policy.get_event_loop().close()

    event_loop = policy.new_event_loop()
    policy.set_event_loop(event_loop)

    def _close():
        event_loop.close()

    request.addfinalizer(_close)
    return event_loop


@pytest.fixture
def event_loop_process_pool(event_loop):
    """Create a fresh instance of the default event loop.

    The event loop will have a process pool set as the default executor."""
    event_loop.set_default_executor(ProcessPoolExecutor())
    return event_loop


@pytest.fixture
def unused_tcp_port():
    """Find an unused localhost TCP port from 1024-65535 and return it."""
    with closing(socket.socket()) as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    return port