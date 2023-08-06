import itertools

import pytest
import slash
from slash._compat import ExitStack, xrange

from .utils import run_tests_assert_success
from .utils.code_formatter import CodeFormatter


def test_fixtures_representation_strings(results, a_values, fixture_values, filename, is_class):
    prefix = '{0}:'.format(filename)
    if is_class:
        prefix += 'Test.'
    assert len(results) == len(a_values) * len(fixture_values)
    assert set(result.test_metadata.address for result in results) == set(
        '{0}test_1(a={1}, fixture=fixture{2})'.format(prefix, i, j) for i, j in itertools.product(a_values, xrange(len(fixture_values))))


@pytest.mark.parametrize('non_printable', ['string/with/slashes', object()])
def test_fixtures_avoid_non_printable_reprs_strs(non_printable):
    with slash.Session():

        @slash.parametrize('param', [non_printable])
        def test_something(param):
            pass

        [loaded_test] = slash.loader.Loader().get_runnables([test_something])

    assert '/' not in loaded_test.__slash__.address
    assert repr(non_printable) not in loaded_test.__slash__.address
    assert str(non_printable) not in loaded_test.__slash__.address


@pytest.fixture
def results(filename):

    with slash.Session() as s:
        tests = slash.loader.Loader().get_runnables(filename)
        session = run_tests_assert_success(tests, session=s)
    return list(session.results.iter_test_results())


@pytest.fixture
def filename(is_class, a_values, fixture_values, tmpdir):
    returned = str(tmpdir.join('testfile.py'))

    with open(returned, 'w') as f:
        with ExitStack() as stack:
            code = CodeFormatter(f)

            code.writeln('import slash')
            code.writeln('@slash.fixture')
            code.writeln(
                '@slash.parametrize("value", {0})'.format(fixture_values))
            code.writeln('def fixture(value):')
            with code.indented():
                code.writeln('return value')

            if is_class:
                code.writeln('class Test(slash.Test):')
                stack.enter_context(code.indented())

            code.writeln('@slash.parametrize("a", {0})'.format(a_values))
            code.write('def test_1(')
            if is_class:
                code.write('self, ')
            code.writeln('a, fixture):')
            with code.indented():
                code.writeln('pass')
    return returned


@pytest.fixture
def a_values():
    return [1, 2, 3]


@pytest.fixture
def fixture_values():
    return [4, 5, 6]


@pytest.fixture(params=[True, False])
def is_class(request):
    return request.param
