import itertools
from contextlib import contextmanager
from uuid import uuid4

from .code_element import CodeElement
from .parameter import Parameter


class Function(CodeElement):

    def __init__(self, suite):
        super(Function, self).__init__(suite)
        self._decorators = []
        self._parameters = []
        self._additional_parameter_string = ""
        self._fixtures = []
        self._deferred_events = []

    def add_parameter_string(self, s):
        self._additional_parameter_string += s

    def add_decorator(self, decorator_string):
        self._decorators.append(decorator_string)

    def get_fixtures(self):
        return self._fixtures

    def get_parameters(self):
        return self._parameters

    def add_parameter(self, *args, **kwargs):
        returned = Parameter(self.suite, *args, **kwargs)
        self._parameters.append(returned)
        return returned

    def depend_on_fixture(self, f):
        self._fixtures.append(f)
        return f

    def _write_event(self, code_formatter, eventcode):
        if self.suite.debug_info:
            code_formatter.writeln(
                '__ut__.events.add({0!r}, {1!r})'.format(
                    eventcode, self.id))

    def add_deferred_event(self, decorator, name='deferred', extra_code=()):
        event = '{0}_{1}'.format(name, uuid4())
        self._deferred_events.append({
            'decorator': decorator, 'event': event, 'extra_code': extra_code})
        return event

    @contextmanager
    def _body_context(self, code_formatter):
        self._write_decorators(code_formatter)
        code_formatter.writeln('def {0}({1}):'.format(
            self._get_function_name(),
            self._get_parameter_string()))

        with code_formatter.indented():
            if not self.suite.debug_info:
                code_formatter.writeln('pass')
            self._write_parameter_values(code_formatter)
            self._write_deferred_events(code_formatter)
            self._write_prologue(code_formatter)
            yield
            self._write_epilogue(code_formatter)
            self._write_return(code_formatter)
        code_formatter.writeln()

    def _get_parameter_string(self):
        returned = ', '.join(self._get_argument_names())
        if returned and self._additional_parameter_string:
            returned += ', '
        returned += self._additional_parameter_string
        return returned

    def _write_prologue(self, code_formatter):
        pass

    def _write_epilogue(self, code_formatter):
        pass

    def _write_deferred_events(self, code_formatter):
        if not self.suite.debug_info:
            return
        for index, deferred in enumerate(self._deferred_events, 1):
            code_formatter.writeln('@{0[decorator]}'.format(deferred))
            code_formatter.writeln('def _defferred{0}():'.format(index))
            with code_formatter.indented():
                code_formatter.writeln('__ut__.events.add({0[event]!r})'.format(deferred))
                for line in deferred['extra_code']:
                    code_formatter.writeln(line)
            code_formatter.writeln()

    def _write_return(self, code_formatter):
        pass

    def _write_decorators(self, code_formatter):
        for d in self._decorators:
            code_formatter.write('@')
            code_formatter.writeln(d)
        for p in self._parameters:
            p.write_decorator(code_formatter)

    def _write_parameter_values(self, code_formatter):
        if not self.suite.debug_info:
            return
        for p in self._parameters:
            code_formatter.writeln('__ut__.notify_parameter_value({0!r}, {1})'.format(
                p.id, p.name))

    def _get_function_name(self):
        raise NotImplementedError()  # pragma: no cover

    @property
    def name(self):
        return self._get_function_name()

    def _get_argument_names(self):
        return (p.name for p in itertools.chain(self._parameters, self._fixtures))
