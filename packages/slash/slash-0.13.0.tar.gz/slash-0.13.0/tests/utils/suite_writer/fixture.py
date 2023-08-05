import itertools
from contextlib import contextmanager

from .function import Function


class Fixture(Function):

    def __init__(self, suite, file, scope=None, autouse=False):
        super(Fixture, self).__init__(suite)
        self.file = file
        self.scope = scope
        self.autouse = autouse

    def add_cleanup(self, **kwargs):
        return self.add_deferred_event('this.add_cleanup', name='fixture_cleanup', **kwargs)

    def _write_decorators(self, code_formatter):
        self._write_fixture_decorator(code_formatter)
        super(Fixture, self)._write_decorators(code_formatter)

    def _get_function_name(self):
        return 'fx_{0}'.format(self.id)

    def _write_prologue(self, code_formatter):
        if not self.suite.debug_info:
            return

        self._write_event(code_formatter, 'fixture_start')
        code_formatter.writeln(
            '__ut__.notify_fixture_start({0!r}, {1})'.format(self.id, self._get_value_string()))
        code_formatter.writeln('@this.add_cleanup')
        code_formatter.writeln('def cleanup():')
        with code_formatter.indented():
            self._write_event(code_formatter, 'fixture_end')
            code_formatter.writeln(
                '__ut__.notify_fixture_end({0!r})'.format(self.id))

        super(Fixture, self)._write_prologue(code_formatter)

    def _write_return(self, code_formatter):
        code_formatter.writeln(
            'return {0}'.format(self._get_value_string()))

    def _write_fixture_decorator(self, code_formatter):

        params = {}
        if self.scope is not None:
            params['scope'] = self.scope
        if self.autouse:
            params['autouse'] = True

        code_formatter.write('@slash.fixture')
        if params:
            code_formatter.write('({0})'.format(', '.join(
                '{0}={1!r}'.format(k, v) for k, v in params.items())))
        code_formatter.writeln()

    def _get_value_string(self):
        returned = '{{"value": {0!r}, "params": {{'.format(self.name)

        for param in itertools.chain(self._parameters, self._fixtures):
            returned += '{0!r}: {1},'.format(param.id, param.name)
        returned += '} }'
        return returned

    def _get_argument_names(self):
        return itertools.chain(['this'], super(Fixture, self)._get_argument_names())

    def __repr__(self):
        return '<Fixture {0}>'.format(self.name)
