import gossip

from .conf import config
from .utils.deprecation import deprecated


def _deprecated_to_gossip(func):
    return deprecated(since="0.6.0", message="Use gossip instead")(func)

def _define(hook_name, **kwargs):
    hook = gossip.define("slash.{0}".format(hook_name), **kwargs)
    globals()[hook_name] = hook
    return hook

_define('session_start', doc="Called right after session starts")
_define('session_end', doc="Called right before the session ends, regardless of the reason for termination")

_define('after_session_start', doc="Second entry point for session start, useful for plugins relying on other plugins' session_start routine")

_define('test_interrupt', doc="Called when a test is interrupted by a KeyboardInterrupt or other similar means")
_define('test_start', doc="Called right after a test starts")
_define('test_end', doc="Called right before a test ends, regardless of the reason for termination")
_define('before_test_cleanups', doc="Called right before a test cleanups are executed")
_define('test_success', doc="Called on test success")
_define('test_error', doc="Called on test error")
_define('test_failure', doc="Called on test failure")
_define('test_skip', doc="Called on test skip", arg_names=("reason",))

_define('error_added', doc='Called when an error is added to a result (either test result or global)', arg_names=('error', 'result'))

_define('result_summary', doc="Called at the end of the execution, when printing results")

_define('exception_caught_before_debugger',
        doc="Called whenever an exception is caught, but a debugger hasn't been entered yet")

_define('exception_caught_after_debugger',
        doc="Called whenever an exception is caught, and a debugger has already been run")

_slash_group = gossip.get_group('slash')
_slash_group.set_strict()
_slash_group.set_exception_policy(gossip.RaiseDefer())

@gossip.register('gossip.on_handler_exception') # pylint: disable=unused-argument
def debugger(handler, exception, hook): # pylint: disable=unused-argument
    from .exception_handling import handle_exception

    if hook.group is _slash_group and config.root.debug.debug_hook_handlers:
        handle_exception(exception)

@_deprecated_to_gossip
def add_custom_hook(hook_name):
    """
    Adds an additional hook to the set of available hooks
    """
    return _define(hook_name)

@_deprecated_to_gossip
def ensure_custom_hook(hook_name):
    """
    Like :func:`.add_custom_hook`, only forgives if the hook already exists
    """
    try:
        return gossip.get_hook("slash.{0}".format(hook_name))
    except LookupError:
        return _define(hook_name)

@_deprecated_to_gossip
def remove_custom_hook(hook_name):
    """
    Removes a hook from the set of available hooks
    """
    gossip.get_hook("slash.{0}".format(hook_name)).undefine()
    globals().pop(hook_name)

@_deprecated_to_gossip
def get_custom_hook_names():
    """
    Retrieves the names of all custom hooks currently installed
    """
    raise NotImplementedError()  # pragma: no cover

@_deprecated_to_gossip
def get_all_hooks():
    return [
        (hook.name, hook)
        for hook in gossip.get_group('slash').get_hooks()]

@_deprecated_to_gossip
def get_hook_by_name(hook_name):
    """
    Returns a hook (if exists) by its name, otherwise returns None
    """
    return gossip.get_hook('slash.{0}'.format(hook_name))
