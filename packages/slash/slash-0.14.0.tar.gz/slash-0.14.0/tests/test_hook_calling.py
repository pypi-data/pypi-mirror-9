from slash._compat import ExitStack
import slash
from slash import plugins
from slash.plugins import PluginInterface
from slash import hooks
import pytest
import gossip

from .utils import TestCase


class SessionEndException(Exception):
    pass


class SessionStartException(Exception):
    pass


class TestEndException(Exception):
    pass


class BeforeTestCleanupException(Exception):
    pass


def test_hook__error_added_during_test(suite, request, checkpoint, suite_test):

    request.addfinalizer(
        hooks.error_added.register(checkpoint)
        .unregister)

    suite_test.when_run.raise_exception()

    summary = suite.run()
    assert checkpoint.called
    [result] = summary.get_all_results_for_test(suite_test)
    assert checkpoint.kwargs['result'] is result


def test_hook__error_added_after_test(suite, request, checkpoint, suite_test):

    request.addfinalizer(
        hooks.error_added.register(checkpoint)
        .unregister)

    summary = suite.run()
    assert not checkpoint.called
    [result] = summary.get_all_results_for_test(suite_test)
    try:
        1/0
    except:
        result.add_error()
    assert checkpoint.called
    assert checkpoint.kwargs['result'] is result
    assert 'ZeroDivisionError' in str(checkpoint.kwargs['error'])



def test_hook__test_interrupt(suite, request, checkpoint):
    request.addfinalizer(
        hooks.test_interrupt.register(checkpoint)
        .unregister)

    test_index = int(len(suite) / 2)
    for index, test in enumerate(suite):
        if index == test_index:
            test.when_run.interrupt()
        elif index > test_index:
            test.expect_deselect()
    suite.run(expect_interruption=True)
    assert checkpoint.called

def test_hook__test_failure_without_exception(suite, request, checkpoint, suite_test):
    request.addfinalizer(
        hooks.test_failure.register(checkpoint)
        .unregister)

    suite_test.append_line('slash.add_failure("failure")')
    suite_test.expect_failure()

    suite.run()
    assert checkpoint.called


@pytest.mark.parametrize(
    'hook_exception', [
        ('slash.session_start', SessionStartException, True),
        ('slash.session_end', SessionEndException, True),
        ('slash.test_end', TestEndException, True),
        ('slash.before_test_cleanups', BeforeTestCleanupException, False)])
@pytest.mark.parametrize('debug_enabled', [True, False])
def test_debugger_called_on_hooks(hook_exception, request, forge, config_override, checkpoint, debug_enabled):
    hook_name, exception_type, should_raise = hook_exception

    @gossip.register(hook_name)
    def raise_exc():
        raise exception_type()

    request.addfinalizer(raise_exc.gossip.unregister)
    config_override("debug.enabled", debug_enabled)

    def test_something():
        pass

    forge.replace_with(slash.utils.debug, 'launch_debugger', checkpoint)

    with ExitStack() as exception_stack:
        if should_raise:
            exception_stack.enter_context(pytest.raises(exception_type))
        with slash.Session() as s:
            with s.get_started_context():
                slash.runner.run_tests(slash.loader.Loader().get_runnables(test_something))

    assert checkpoint.called == debug_enabled
    if debug_enabled:
        assert checkpoint.args[0][0] is exception_type
        assert type(checkpoint.args[0][1]) is exception_type


def test_before_cleanup_hook(request, forge):
    cleanup = forge.create_wildcard_function_stub(name='cleanup')
    before_cleanup_hook = forge.create_wildcard_function_stub(name='before_test_cleanup')
    test_end_hook = forge.create_wildcard_function_stub(name='test_end')
    gossip.register(before_cleanup_hook, 'slash.before_test_cleanups')
    gossip.register(test_end_hook, 'slash.test_end')

    request.addfinalizer(before_cleanup_hook.gossip.unregister)
    request.addfinalizer(test_end_hook.gossip.unregister)

    before_cleanup_hook()
    cleanup()
    test_end_hook()

    forge.replay()

    def test_something():
        slash.add_cleanup(cleanup)

    with slash.Session() as s:
        with s.get_started_context():
            slash.runner.run_tests(slash.loader.Loader().get_runnables(test_something))


#### Older tests below, need modernizing ####

class HookCallingTest(TestCase):

    def setUp(self):
        super(HookCallingTest, self).setUp()
        self.plugin1 = make_custom_plugin("plugin1", self)
        self.plugin2 = make_custom_plugin("plugin2", self, hook_names=["session_start", "after_session_start"])
        self.addCleanup(plugins.manager.uninstall, self.plugin1)
        self.addCleanup(plugins.manager.uninstall, self.plugin2)

    def test_hook_calling_order(self):
        # expect:
        with self.forge.any_order():
            self.plugin1.activate()
            self.plugin2.activate()

        with self.forge.any_order():
            self.plugin1.session_start()
            self.plugin2.session_start()


        with self.forge.any_order():
            self.plugin1.after_session_start()
            self.plugin2.after_session_start()

        self.plugin1.session_end()

        self.forge.replay()
        # get:

        plugins.manager.install(self.plugin1, activate=True)
        plugins.manager.install(self.plugin2, activate=True)

        with slash.Session() as s:
            with s.get_started_context():
                pass


def make_custom_plugin(name, test, hook_names=None):

    class CustomPlugin(PluginInterface):
        def get_name(self):
            return name

    CustomPlugin.__name__ = name

    if hook_names is None:
        hook_names = [name for name, _ in slash.hooks.get_all_hooks()]

    for hook_name in hook_names:
        setattr(CustomPlugin, hook_name, test.forge.create_wildcard_function_stub(name=hook_name))

    setattr(CustomPlugin, "activate", test.forge.create_wildcard_function_stub(name="activate"))

    return CustomPlugin()
