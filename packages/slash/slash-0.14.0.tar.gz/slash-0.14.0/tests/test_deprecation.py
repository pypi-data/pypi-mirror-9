import logbook

import pytest
from slash.utils.deprecation import deprecated


def test_deprecated_func_called(capture):
    assert deprecated_func(1, 2) == 3

def test_deprecation_message(capture):
    deprecated_func(1, 2)

    [record] = capture.records
    assert "deprecated" in record.message
    assert 'deprecated_func' in record.message

def test_deprecation_with_message(capture):

    @deprecated("use something else instead", since="1.0.0")
    def func(a, b):
        return a + b

    func(1, 2)

    [record] = capture.records
    assert "use something else instead" in record.message
    assert "func is deprecated" in record.message

def test_deprecations_different_sources(capture):

    def f():
        deprecated_func(1, 2)

    def g():
        deprecated_func(1, 2)

    f()
    g()
    assert len(capture.records) == 2

def test_deprecations_same_sources(capture):

    def f():
        deprecated_func(1, 2)

    f()
    f()
    assert len(capture.records) == 1

def test_deprecatd_docstring():

    message = "Use something else instead"

    @deprecated(since="1.0.0")
    def some_func():
        """This is a function
        """

    @deprecated(message, since="1.0.0")
    def other_func():
        """This is another function
        """

    assert ".. deprecated:: 1.0.0" in some_func.__doc__
    assert ".. deprecated:: 1.0.0\n   {0}".format(message) in other_func.__doc__


@pytest.fixture
def capture(request):
    handler = logbook.TestHandler(level=logbook.WARNING)
    handler.push_application()

    @request.addfinalizer
    def pop():
        handler.pop_application()
    return handler

@deprecated(since="1.0.0")
def deprecated_func(a, b):
    return a + b
