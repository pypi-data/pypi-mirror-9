import functools

from ..ctx import context
from ..exceptions import SkipTest


def skip_test(*args):
    """
    Skips the current test execution by raising a :class:`slash.exceptions.SkipTest`
    exception. It can optionally receive a reason argument.
    """
    raise SkipTest(*args)


def skipped(thing, reason=None):
    """
    A decorator for skipping methods and classes
    """
    from ..core.test import Test

    if isinstance(thing, str):
        return functools.partial(skipped, reason=thing)
    if isinstance(thing, type) and issubclass(thing, Test):
        thing.skip_all(reason)
        return thing

    @functools.wraps(thing)
    def new_func(*_, **__):  # pylint: disable=unused-argument
        skip_test(reason)
    return new_func


def add_error(msg):
    """
    Adds an error to the current test result

    :param msg: can be either an object or a string representing a message
    """
    if context.session is not None:
        context.session.results.current.add_error(msg)


def add_failure(msg):
    """
    Adds a failure to the current test result

    :param msg: can be either an object or a string representing a message
    """
    if context.session is not None:
        context.session.results.current.add_failure(msg)


def set_test_detail(key, value):
    """
    Store an object providing additional information about the current running test in a certain key.
    Each test has its own storage.

    :param key: a hashable object
    :param value: can be either an object or a string representing additional details
    """
    if context.session is not None:
        context.session.results.current.set_test_detail(key, value)
