import collections
import functools
import itertools

import pytest
import slash
from slash._compat import iteritems
from slash.core.fixtures.fixture_scope_manager import FixtureScopeManager
from slash.loader import Loader


def test_scope_manager(dummy_fixture_store, scope_manager, tests_by_module):
    last_scopes = None
    for module_index, tests in enumerate(tests_by_module):
        for test_index, test in enumerate(tests):
            scope_manager.begin_test(test)
            assert dummy_fixture_store._scopes == ['session', 'module', 'test']
            expected = _increment_scope(
                last_scopes,
                test=1,
                module=1 if test_index == 0 else 0,
                session=1 if test_index == 0 and module_index == 0 else 0)
            assert dummy_fixture_store._scope_ids == expected
            # make sure the dict is copied
            assert expected is not dummy_fixture_store._scope_ids
            last_scopes = expected
            if test_index != len(tests) - 1:
                next_test = tests[test_index + 1]
                end_of_module = False
            elif module_index != len(tests_by_module) - 1:
                next_test = tests_by_module[module_index + 1][1]
                end_of_module = True
            else:
                next_test = None
            scope_manager.end_test(test, next_test=next_test)
            if next_test is None:
                assert dummy_fixture_store._scopes == []
            elif end_of_module:
                assert dummy_fixture_store._scopes == ['session']
            else:
                assert dummy_fixture_store._scopes == ['session', 'module']
            assert dummy_fixture_store._scope_ids == last_scopes


@pytest.fixture
def scope_manager(dummy_fixture_store):
    return FixtureScopeManager(dummy_fixture_store)


@pytest.fixture
def dummy_fixture_store():
    return DummyFixtureStore()


@pytest.fixture
def tests_by_module():

    def test_func():
        pass

    num_modules = 5
    num_tests_per_module = 3
    returned = []

    with slash.Session():
        for module_index in range(num_modules):
            module_name = '__module_{0}'.format(module_index)
            returned.append([])
            for test_index in range(num_tests_per_module):
                [test] = Loader().get_runnables([test_func])
                assert not test.__slash__.module_name
                test.__slash__.module_name = module_name
                returned[-1].append(test)
    return returned


def _increment_scope(prev_scopes, **increments):
    if not prev_scopes:
        returned = {}
    else:
        returned = prev_scopes.copy()
    for key, value in iteritems(increments):
        if value == 0:
            continue
        if key not in returned:
            returned[key] = 0
        returned[key] += value
    return returned


class DummyFixtureStore(object):

    def __init__(self):
        super(DummyFixtureStore, self).__init__()
        self._scopes = []
        self._counters = collections.defaultdict(
            functools.partial(itertools.count, 1))
        self._scope_ids = {}

    def begin_scope(self, scope):
        self._scopes.append(scope)
        self._scope_ids[scope] = next(self._counters[scope])

    def end_scope(self, scope):
        latest_scope = self._scopes.pop()
        assert latest_scope == scope
