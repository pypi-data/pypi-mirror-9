# pylint: disable=import-error,no-name-in-module
from __future__ import division
import collections
import itertools
import sys

from py.io import TerminalWriter
from textwrap import wrap

from .._compat import iteritems, izip
from ..conf import config
from ..log import VERBOSITIES
from ..utils.iteration import iteration
from ..utils.python import wraps
from .reporter_interface import ReporterInterface

# traceback levels
NO_TRACEBACK, SINGLE_FRAME, ALL_FRAMES, ALL_FRAMES_WITH_CONTEXT, ALL_FRAMES_WITH_CONTEXT_AND_VARS = range(
    5)


def from_verbosity(level):
    def decorator(func):
        @wraps(func)
        def new_func(self, *args, **kwargs):
            if self._verobsity_allows(level):  # pylint: disable=protected-access
                return func(self, *args, **kwargs)

        return new_func
    return decorator


class TerminalWriterWrapper(object):

    def __init__(self, file):
        super(TerminalWriterWrapper, self).__init__()
        self._writer = TerminalWriter(file=file)
        self._line = ''

    def _get_full_width(self):
        fullwidth = self._writer.fullwidth
        if sys.platform == "win32":
            # see py.io documentation for an explanation
            fullwidth -= 1

        return fullwidth

    def lsep(self, sep, msg, **kw):
        """Write a left-justified line filled with the separator until the end of the line"""

        self._do_write(
            '{0} {1}\n'.format(msg, sep * ((self._get_full_width() - 1 - len(msg)) // len(sep))), **kw)

    def write_box(self, headline, msg, **kw):
        box_width = min(self._get_full_width(), 60)
        line_width = box_width - 4

        max_headline_length = box_width - 6
        if len(headline) > max_headline_length:
            headline = headline[max_headline_length:]

        def write_line(line_to_write):
            eol_padding = box_width - (len(line_to_write) + 3)
            self._do_write('* {0}{1}*\n'.format(line_to_write, ' ' * eol_padding), **kw)  # pylint: disable=star-args

        self._do_write('\n** {0} {1}\n'.format(headline, '*' * (box_width - (len(headline) + 4))), **kw)  # pylint: disable=star-args
        for line in msg.split('\n'):
            if not line:
                write_line('')
            else:
                for sub_line in wrap(line, line_width):
                    write_line(sub_line)
        self._do_write('{0}\n\n'.format('*' * box_width), **kw)

    def sep(self, *args, **kw):
        self._line = ''
        return self._writer.sep(*args, **kw)

    def write(self, line, **kw):
        line = str(line)
        self._do_write(line, **kw)
        self._line = self._get_line_remainder(line)

    def _get_line_remainder(self, line):
        return line.rsplit('\r', 1)[-1].rsplit('\n', 1)[-1]

    def line(self, *args, **kw):
        self._writer.line(*args, **kw)
        self._line = ''

    def get_line_in_progress(self):
        return self._line

    def clear_line_in_progress(self):
        if self._line and self._writer.hasmarkup:
            self._do_write('\r')
            self._do_write(' ' * len(self._line))
            self._do_write('\r')

    def restore_line_in_progress(self):
        if self._writer.hasmarkup:
            self._do_write(self._line)

    def _do_write(self, *args, **kwargs):
        return self._writer.write(*args, **kwargs)


class ConsoleReporter(ReporterInterface):

    def __init__(self, level, stream=sys.stderr):
        super(ConsoleReporter, self).__init__()
        self._level = level
        self._stream = stream
        self._terminal = TerminalWriterWrapper(file=stream)

    def notify_before_console_output(self):
        self._terminal.clear_line_in_progress()

    def notify_after_console_output(self):
        self._terminal.restore_line_in_progress()

    def report_before_debugger(self, exc_info):
        self.notify_before_console_output()
        self._terminal.write('Exception caught in debugger: {0} {1}\n'.format(
            exc_info[0], exc_info[1]), red=True)
        self.notify_after_console_output()

    def report_collection_start(self):
        self._report_num_collected([], stillworking=True)

    def report_test_collected(self, all_tests, test):
        self._report_num_collected(all_tests, stillworking=True)

    def report_collection_end(self, collected):
        self._report_num_collected(collected, stillworking=False)

    def _report_num_collected(self, collected, stillworking):
        self._terminal.write('\r{0} tests collected{1}'.format(
            len(collected), '...' if stillworking else '   \n'), white=True, bold=True)

    def _is_verbose(self, level):
        return self._level <= level

    @from_verbosity(VERBOSITIES.ERROR)
    def report_session_start(self, session):
        self._terminal.sep('=', 'Session starts', white=True, bold=True)

    def report_session_end(self, session):

        if not self._verobsity_allows(VERBOSITIES.WARNING):
            # for concise outputs we need to break the sequence of dots...
            self._terminal.write('\n')

        header_format = self._get_session_summary_header_format(session)

        for index, (test_index, test_result, infos) in enumerate(self._iter_reported_results(session)):
            if index == 0:
                self._terminal.sep('=', 'Session Summary', **header_format)   # pylint: disable=star-args
            self._report_test_summary_header(test_index, test_result)
            self._report_additional_test_details(test_result)
            for info_reporter in infos:
                info_reporter(test_result)

        if self._verobsity_allows(VERBOSITIES.WARNING):
            self._report_result_warning_summary(session)

        msg = 'Session ended.'
        msg += ' {0} successful, {1} skipped, {2} failures, {3} errors.'.format(
            session.results.get_num_successful(
            ), session.results.get_num_skipped(),
            session.results.get_num_failures(), session.results.get_num_errors())

        msg += ' Total duration: {0}'.format(
            self._format_duration(session.duration))
        self._terminal.sep('=', msg, **header_format)  # pylint: disable=star-args

    def _get_session_summary_header_format(self, session):
        returned = {'bold': True}
        if session.results.is_success(allow_skips=True):
            returned.update(green=True)
        else:
            returned.update(red=True)
        return returned

    def _iter_reported_results(self, session):
        for test_index, test_result in enumerate(session.results.iter_test_results()):
            infos = self._get_result_info_generators(test_result)
            if not infos:
                continue
            yield test_index, test_result, infos

    def _report_test_summary_header(self, index, test_result):
        self._terminal.lsep(
            "=", '== #{0}: {1}'.format(index + 1, test_result.test_metadata.address))

    def _get_result_info_generators(self, test_result):
        returned = []
        if self._verobsity_allows(VERBOSITIES.ERROR) and test_result.has_errors_or_failures():
            returned.append(self._report_result_errors_failures)
        if self._verobsity_allows(VERBOSITIES.INFO) and test_result.has_skips():
            returned.append(self._report_result_skip_summary)

        return returned

    def _report_result_warning_summary(self, session):
        warnings_by_key = collections.defaultdict(list)
        for warning in session.warnings:
            warnings_by_key[warning.key].append(warning)
        for i, (warning_key, warnings) in iteration(iteritems(warnings_by_key)):
            if i.first:
                self._terminal.sep(
                    '=', 'Warnings ({0} total)'.format(len(session.warnings)), yellow=True)
            self._terminal.write(
                ' * {d[filename]}:{d[lineno]:03} -- '.format(d=warnings[0].details), yellow=True)
            self._terminal.write(
                warnings[0].details['message'], yellow=True, bold=True)
            self._terminal.write(
                ' (Repeated {0} times)\n'.format(len(warnings)), yellow=True)

    def _verobsity_allows(self, level):
        return self._level <= level

    def _report_result_errors_failures(self, test_result):
        all_errs = list(
            itertools.chain(izip(itertools.repeat("E"), test_result.get_errors()),
                            izip(itertools.repeat("F"), test_result.get_failures())))
        for index, (err_type, err) in enumerate(all_errs):
            err_header = ' - {0}/{1} {2} ({3:YYYY-MM-DD HH:mm:ss ZZ}): {4}'.format(
                index + 1,
                len(all_errs),
                err_type,
                err.time.to('local'),
                ' - {0}'.format(err.message) if not err.traceback else '')
            self._terminal.lsep(' -', err_header, red=True)
            self._report_traceback(err_type, err)

    def _report_traceback(self, err_type, err):
        traceback_level = config.root.log.traceback_level
        if not err.traceback or traceback_level == NO_TRACEBACK:
            frames = []
        elif traceback_level == SINGLE_FRAME:
            frames = [err.traceback.frames[-1]]
        else:
            frames = err.traceback.frames
        for frame_iteration, frame in iteration(frames):
            self._terminal.write(
                '  {0}:{1}:\n'.format(frame.filename, frame.lineno), black=True, bold=True)
            if traceback_level >= ALL_FRAMES_WITH_CONTEXT_AND_VARS:
                if not frame_iteration.first:
                    self._terminal.sep('- ')
                self._write_frame_locals(frame)
            code_lines = self._write_frame_code(
                frame, include_context=(traceback_level >= ALL_FRAMES_WITH_CONTEXT))
            if frame_iteration.last:
                self._terminal.write(err_type, red=True, bold=True)
                if code_lines:
                    indent = ''.join(
                        itertools.takewhile(str.isspace, code_lines[-1]))
                else:
                    indent = ''
                self._terminal.write(
                    self._indent_with(err.message, indent), red=True, bold=True)
                self._terminal.write('\n')

    def _report_additional_test_details(self, result):
        if result.is_success():
            return
        detail_items = iteritems(result.get_additional_details())

        log_path = result.get_log_path()
        if log_path is not None:
            detail_items = itertools.chain(detail_items, [('Log', log_path)])

        for index, (key, value) in enumerate(detail_items):
            if index == 0:
                self._terminal.write(' - Additional Details:\n', black=True, bold=True)
            self._terminal.write('    > {0}: {1!r}\n'.format(key, value), black=True, bold=True)

    def _indent_with(self, text, indent):
        return '\n'.join(indent + line for line in text.splitlines())

    def _report_result_skip_summary(self, result):
        self._terminal.write('\tSkipped ({0})\n'.format(result.get_skips()[0]), yellow=True)

    def _write_frame_locals(self, frame):
        if not frame.locals and not frame.globals:
            return
        for index, (name, value) in enumerate(itertools.chain(iteritems(frame.locals), iteritems(frame.globals))):
            if index > 0:
                self._terminal.write(', ')
            self._terminal.write(
                '    {0}: '.format(name), yellow=True, bold=True)
            self._terminal.write(value['value'])
        self._terminal.write('\n\n')

    def _write_frame_code(self, frame, include_context):
        if frame.code_string:
            if include_context:
                code_lines = frame.code_string.splitlines()
            else:
                code_lines = [frame.code_line]
            line = ''
            for line_iteration, line in iteration(code_lines):
                if line_iteration.last:
                    self._terminal.write('>', white=True, bold=True)
                else:
                    self._terminal.write(' ')
                self._terminal.write(line, white=True, bold=True)
                self._terminal.write('\n')
            return code_lines

    @from_verbosity(VERBOSITIES.WARNING)
    def report_file_start(self, filename):
        self._file_failed = False
        self._file_has_skips = False
        if not self._verobsity_allows(VERBOSITIES.NOTICE):
            self._terminal.write(filename)
            self._terminal.write(' ')

    @from_verbosity(VERBOSITIES.WARNING)
    def report_file_end(self, filename):
        if self._verobsity_allows(VERBOSITIES.NOTICE):
            return
        self._terminal.write('  ')
        if self._file_failed:
            self._terminal.line('FAIL', red=True)
        elif self._file_has_skips:
            self._terminal.line('PASS', yellow=True)
        else:
            self._terminal.line('PASS', green=True)

    def report_test_success(self, test, result):
        if not self._verobsity_allows(VERBOSITIES.NOTICE):
            self._terminal.write('.')

    def report_test_skip_added(self, test, reason):
        self._file_has_skips = True
        if self._verobsity_allows(VERBOSITIES.NOTICE):
            self._terminal.write('Skipped: {0}\n'.format(reason), yellow=True)
        else:
            self._terminal.write('s', yellow=True)

    def report_test_error_added(self, test, error):
        self._report_test_error_failure_added(test, error, 'E')

    def report_test_failure_added(self, test, error):
        self._report_test_error_failure_added(test, error, 'F')

    def _report_test_error_failure_added(self, test, e, errtype):
        self._file_failed = True
        if not self._verobsity_allows(VERBOSITIES.NOTICE):
            self._terminal.write(errtype, red=True)
        else:
            self._terminal.write('{0}: {1}\n'.format(errtype, e), red=True)

    def report_fancy_message(self, headline, message):
        if self._verobsity_allows(VERBOSITIES.INFO):
            self._terminal.write_box(headline, message, bold=True, yellow=True)

    def report_message(self, message):
        self.notify_before_console_output()
        self._terminal.write(message)
        self._terminal.write('\n')
        self.notify_after_console_output()

    def _format_duration(self, duration):
        seconds = duration % 60
        duration /= 60
        minutes = duration % 60
        hours = duration / 60
        return '{0:02}:{1:02}:{2:02}'.format(int(hours), int(minutes), int(seconds))
