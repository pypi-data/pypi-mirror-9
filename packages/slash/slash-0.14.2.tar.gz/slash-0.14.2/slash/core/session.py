import itertools
import sys
import time
import uuid
from contextlib import contextmanager

from .. import ctx, hooks, log
from ..exception_handling import handling_exceptions
from ..interfaces import Activatable
from ..reporting.null_reporter import NullReporter
from ..utils.id_space import IDSpace
from ..utils.interactive import notify_if_slow_context
from ..warnings import SessionWarnings
from .fixtures.fixture_store import FixtureStore
from .result import SessionResults


class Session(Activatable):
    """ Represents a slash session
    """

    duration = start_time = end_time = None

    def __init__(self, reporter=None):
        super(Session, self).__init__()
        self.id = "{0}_0".format(uuid.uuid1())
        self.id_space = IDSpace(self.id)
        self.test_index_counter = itertools.count()
        self._started = False
        self._complete = False
        self._active_context = None
        self.fixture_store = FixtureStore()
        self.warnings = SessionWarnings()
        self.logging = log.SessionLogging(self)
        #: an aggregate result summing all test results and the global result
        self.results = SessionResults(self)
        if reporter is None:
            reporter = NullReporter()
        self.reporter = reporter

    @property
    def started(self):
        return self._started

    def activate(self):
        with handling_exceptions():
            ctx.push_context()
            assert ctx.context.session is None
            assert ctx.context.result is None
            ctx.context.session = self
            ctx.context.result = self.results.global_result
            self._logging_context = self.logging.get_session_logging_context()
            self._logging_context.__enter__()

    def deactivate(self):
        self.results.global_result.mark_finished()
        with handling_exceptions():
            self._logging_context.__exit__(*sys.exc_info())
            self._logging_context = None
            ctx.pop_context()

    @contextmanager
    def get_started_context(self):
        self.start_time = time.time()
        try:
            with handling_exceptions():
                with notify_if_slow_context("Initializing session..."):
                    hooks.session_start()  # pylint: disable=no-member
            hooks.after_session_start()  # pylint: disable=no-member
            self._started = True
            yield
        finally:
            self._started = False
            self.end_time = time.time()
            self.duration = self.end_time - self.start_time

            with handling_exceptions():
                hooks.session_end()  # pylint: disable=no-member
            self.reporter.report_session_end(self)

    def mark_complete(self):
        self._complete = True

    def is_complete(self):
        return self._complete
