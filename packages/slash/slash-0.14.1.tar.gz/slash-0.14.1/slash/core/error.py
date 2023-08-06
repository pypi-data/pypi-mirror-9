import arrow
import sys
import traceback

from .._compat import string_types, StringIO, iteritems
from ..exception_handling import is_exception_fatal
from ..utils.traceback_utils import distill_traceback, distill_call_stack
from ..utils.formatter import Formatter


class Error(object):

    traceback = exception_type = exception = arg = _cached_detailed_traceback_str = None

    def __init__(self, msg=None, exc_info=None, frame_correction=0):
        super(Error, self).__init__()
        self.time = arrow.utcnow()
        if msg is None and exc_info is not None:
            msg = traceback.format_exception_only(exc_info[0], exc_info[1])[0].strip()
        if not isinstance(msg, string_types):
            self.arg = msg
            msg = repr(msg)
        self.message = msg
        if exc_info is not None:
            self.exception_type, self.exception, tb = exc_info  # pylint: disable=unpacking-non-sequence
            self.traceback = distill_traceback(tb, frame_correction=frame_correction)
        else:
            self.traceback = distill_call_stack(frame_correction=frame_correction+4)

    def is_fatal(self):
        return self.exception is not None and is_exception_fatal(self.exception)

    @classmethod
    def capture_exception(cls):
        _, exc_value, _ = exc_info = sys.exc_info()
        cached = getattr(exc_value, "__slash_captured_error__", None)
        if cached is not None:
            return cached
        returned = exc_value.__slash_captured_error__ = cls(exc_info=exc_info)
        return returned

    @property
    def cause(self):
        if self.traceback is not None:
            return self.traceback.cause

    @property
    def filename(self):
        if self.traceback is not None:
            return self.traceback.cause.filename

    @property
    def lineno(self):
        if self.traceback is not None:
            return self.traceback.cause.lineno

    @property
    def func_name(self):
        if self.traceback is not None:
            return self.traceback.cause.func_name

    def __repr__(self):
        return self.message

    def get_detailed_traceback_str(self):
        if self._cached_detailed_traceback_str is None:
            stream = StringIO()
            f = Formatter(stream, indentation_string='  ')
            f.writeln("Traceback (most recent call last):")
            with f.indented():
                for frame in self.traceback.frames:
                    f.writeln('File "{f.filename}", line {f.lineno}, in {f.func_name}:'.format(f=frame))
                    with f.indented():
                        f.writeln('>', frame.code_line.strip() or '?')
                        with f.indented():
                            for title, vars in [('globals', frame.globals), ('locals', frame.locals)]:
                                for index, (var_name, var_repr) in enumerate(iteritems(vars)):
                                    if index == 0:
                                        f.writeln(title)
                                        f.indent()
                                    f.writeln(' - {0}: {1}'.format(var_name, var_repr['value']))
                            f.dedent()
            self._cached_detailed_traceback_str = stream.getvalue()

        return self._cached_detailed_traceback_str

    def get_detailed_str(self):
        return '{0}*** {1}'.format(
            self.get_detailed_traceback_str(), self)

