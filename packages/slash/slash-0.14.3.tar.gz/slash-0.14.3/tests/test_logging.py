import functools
import os

import logbook

import gossip
import pytest
import slash

from .utils import run_tests_assert_success, run_tests_in_session, TestCase


def test_last_session_symlinks(files_dir, links_dir, session):

    test_log_file = files_dir.join(
        session.id, list(session.results.iter_test_results())[-1].test_metadata.id, "log")
    assert test_log_file.check()
    session_log_file = files_dir.join(session.id, "session.log")
    assert session_log_file.check()

    assert links_dir.join("last-session").readlink() == session_log_file
    assert links_dir.join("last-session-dir").readlink() == session_log_file.dirname
    assert links_dir.join("last-test").readlink() == test_log_file


def test_global_result_get_log_path(files_dir, suite):
    summary = suite.run()
    assert summary.session.results.global_result.get_log_path() is not None
    assert summary.session.results.global_result.get_log_path().startswith(str(files_dir))


def test_log_file_colorize(files_dir, config_override, suite):
    config_override('log.colorize', True)
    summary = suite.run()
    logfile = summary.session.results.global_result.get_log_path()
    with open(logfile, 'rb') as f:
        log_data = f.read()

    assert b'\x1b[' in log_data


@pytest.mark.parametrize('level', ['info', 'notice', 'warning'])
def test_console_truncation_does_not_truncate_files(files_dir, suite, suite_test, config_override, level):
    assert slash.config.root.log.truncate_console_lines

    long_string = 'a' * 1000
    suite_test.append_line('slash.logger.{level}({msg!r})'.format(msg=long_string, level=level))
    summary = suite.run()
    [result] = summary.get_all_results_for_test(suite_test)
    with open(result.get_log_path()) as logfile:
        logfile_data = logfile.read()
        assert long_string in logfile_data


@pytest.mark.parametrize('symlink_name', ['last_session_symlink', 'last_session_dir_symlink', 'last_failed_symlink'])
def test_log_symlinks_without_root_path(suite, config_override, symlink_name):
    config_override('log.{0}'.format(symlink_name), 'some/subdir')
    assert suite.run().ok()


def test_last_test_not_overriden_by_stop_on_error(links_dir, suite):
    failed_test = suite[4]
    failed_test.when_run.fail()
    # we stop on error...
    for test in suite[5:]:
        test.expect_skip()
    summary = suite.run(additional_args=['-x'])

    [failed_result] = summary.get_all_results_for_test(failed_test)

    for link_name in ('last-test', 'last-failed'):
        assert links_dir.join(link_name).readlink() == failed_result.get_log_path()


def test_result_log_links(files_dir, session):

    for result in session.results.iter_test_results():
        assert result.get_log_path() is not None
        assert result.get_log_path().startswith(str(files_dir))


def test_last_failed(suite, links_dir):
    suite[-5].when_run.fail()
    last_failed = suite[-2]
    last_failed.when_run.fail()
    summary = suite.run()

    [result] = summary.get_all_results_for_test(last_failed)
    fail_log = result.get_log_path()
    assert os.path.isfile(fail_log)
    assert links_dir.join('last-failed').readlink() == fail_log


@pytest.fixture
def session():
    session = run_tests_assert_success(SampleTest)
    return session


@pytest.fixture
def files_dir(logs_dir):
    return logs_dir.join("files")


@pytest.fixture
def links_dir(logs_dir):
    return logs_dir.join("links")


@pytest.fixture
def logs_dir(request, config_override, tmpdir, relative_symlinks):
    returned = tmpdir.join('logs')
    config_override("log.root", str(returned.join("files")))
    config_override("log.last_session_symlink",
                    str("../links/last-session" if relative_symlinks else returned.join("links", "last-session")))
    config_override("log.last_session_dir_symlink",
                    str("../links/last-session-dir" if relative_symlinks else returned.join("links", "last-session-dir")))
    config_override("log.last_test_symlink",
                    str("../links/last-test" if relative_symlinks else returned.join("links", "last-test")))
    config_override("log.last_failed_symlink",
                    str("../links/last-failed" if relative_symlinks else returned.join("links", "last-failed")))

    return returned


@pytest.fixture(params=[True, False])
def relative_symlinks(request):
    return request.param


@pytest.fixture
def links_dir(logs_dir):
    return logs_dir.join("links")


@pytest.fixture
def files_dir(logs_dir):
    return logs_dir.join("files")


_TOKEN = "logging-test"
_SESSION_START_MARK = "session-start-mark"
_SESSION_END_MARK = "session-end-mark"

_silenced_logger = logbook.Logger("silenced_logger")


class LogFormattingTest(TestCase):

    def setUp(self):
        super(LogFormattingTest, self).setUp()
        self.log_path = self.get_new_path()
        self.override_config(
            "log.root", self.log_path
        )
        self.override_config(
            "log.format", "-- {record.message} --"
        )
        self.override_config("log.subpath", "debug.log")

    def test(self):
        self.session = run_tests_assert_success(SampleTest)
        with open(os.path.join(self.log_path, "debug.log")) as logfile:
            for line in logfile:
                self.assertTrue(line.startswith("-- "))
                self.assertTrue(line.endswith(" --\n"))


class LoggingTest(TestCase):

    def test(self):
        self.log_path = self.get_new_path()
        self.override_config(
            "log.root",
            self.log_path,
        )
        self.override_config(
            "log.subpath",
            os.path.join("{context.session.id}",
                         "{context.test.__slash__.test_index0:03}-{context.test_id}", "debug.log")
        )
        self.override_config(
            "log.session_subpath",
            os.path.join("{context.session.id}", "debug.log")
        )
        self.override_config(
            "log.silence_loggers",
            [_silenced_logger.name]
        )

        self.addCleanup(gossip.unregister_token, _TOKEN)
        slash.hooks.session_start.register(
            functools.partial(_mark, _SESSION_START_MARK), token=_TOKEN)

        slash.hooks.session_end.register(
            functools.partial(_mark, _SESSION_END_MARK), token=_TOKEN)
        self.addCleanup(gossip.unregister_token, _TOKEN)

        self.session = run_tests_assert_success(SampleTest)
        self.tests_metadata = [
            result.test_metadata for result in self.session.results.iter_test_results()]
        self._test_all_run()
        self._test_test_logs_written()
        self._test_session_logs()
        self._test_no_silenced_logger_records()

    def _test_all_run(self):
        methods = [
            method_name for method_name in dir(SampleTest)
            if method_name.startswith("test")
        ]
        self.assertTrue(methods)
        self.assertEquals(len(self.tests_metadata), len(methods))

    def _test_test_logs_written(self):
        for test_metadata in self.tests_metadata:
            test_dir = "{0:03}-{1}".format(test_metadata.test_index0, test_metadata.id)
            log_path = os.path.join(
                self.log_path, self.session.id, test_dir, "debug.log")
            with open(log_path) as f:
                data = f.read()
            for other_test in self.tests_metadata:
                if other_test.id != test_metadata.id:
                    self.assertNotIn(other_test.id, data)
            self.assertNotIn(_SESSION_START_MARK, data)
            self.assertNotIn(_SESSION_END_MARK, data)

    def _test_session_logs(self):
        with open(os.path.join(self.log_path, self.session.id, "debug.log")) as f:
            data = f.read()
        self.assertIn(_SESSION_START_MARK, data)
        self.assertIn(_SESSION_END_MARK, data)
        for test_id in (t.id for t in self.tests_metadata):
            self.assertNotIn(test_id, data)

    def _test_no_silenced_logger_records(self):
        for path, _, filenames in os.walk(self.log_path):
            for filename in filenames:
                assert filename.endswith(".log")
                filename = os.path.join(path, filename)
                with open(filename) as f:
                    assert _silenced_logger.name not in f.read(
                    ), "Silenced logs appear in log file {0}".format(filename)


class ExtraLoggersTest(TestCase):

    def setUp(self):
        super(ExtraLoggersTest, self).setUp()
        self.session = slash.Session()
        self.handler = logbook.TestHandler()
        self.addCleanup(slash.log.remove_all_extra_handlers)
        slash.log.add_log_handler(self.handler)

    def test(self):
        with self.session:
            run_tests_in_session(SampleTest, session=self.session)
        for test_result in self.session.results.iter_test_results():
            for record in self.handler.records:
                if test_result.test_id in record.message:
                    break
            else:
                self.fail(
                    "Test id {} does not appear in logger".format(test_result.test_id))


class SampleTest(slash.Test):

    def test_1(self):
        _mark()

    def test_2(self):
        _silenced_logger.error("error")
        _silenced_logger.info("info")
        _silenced_logger.debug("debug")
        _mark()


def _mark(text=None):
    if text is None:
        text = slash.context.test_id
    slash.logger.debug(text)


class TestLocaltimeLogging(TestCase):

    def setUp(self):
        super(TestLocaltimeLogging, self).setUp()
        self.assertFalse(slash.config.root.log.localtime)
        self.path = self.get_new_path()
        self.override_config(
            "log.localtime", True)
        self.override_config(
            "log.root", self.path)

    def test_local_time(self):
        with slash.Session() as s:
            slash.logger.info("Hello")
        self.assertNotEquals(os.listdir(self.path), [])
