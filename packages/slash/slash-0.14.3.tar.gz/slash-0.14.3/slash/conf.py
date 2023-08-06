import logbook
from confetti import Config
from .utils.conf_utils import Doc, Cmdline

__all__ = ["config"]

config = Config({
    "debug": {
        "debug_skips": False // Doc("Enter pdb also for SkipTest exceptions"),
        "debug_hook_handlers": False // Doc("Enter pdb also for every exception encountered in a hook/callback. Only relevant when debugging is enabled"),
        "enabled": False // Doc("Enter pdb on failures and errors") // Cmdline(on="--pdb"),
    },
    "log": {
        "colorize": False // Doc("Emit log colors to files"),
        "console_level": logbook.WARNING // Doc("console log level (can be repeated). Higher log level means quieter output.") // Cmdline(decrease="-v", increase="-q"),
        "traceback_level": 4 // Doc("Detail level of tracebacks") // Cmdline(arg="--tb"),
        "truncate_console_lines": True // Doc("truncate long log lines on the console") // Cmdline(arg='--truncate-console-lines', metavar='yes/no'),
        "truncate_console_errors": False // Doc("If truncate_console_lines is set, also truncate long log lines, including and above the \"error\" level, on the console"),
        "root": None // Doc("Root directory for logs") // Cmdline(arg="-l", metavar="DIR"),
        "subpath": "{context.session.id}/{context.test_id}/log" // Doc("Path to write logs to under the root"),
        "session_subpath": "{context.session.id}/session.log",
        "last_session_symlink": None // Doc("If set, specifies a symlink path to the last session log file in each run"),
        "last_session_dir_symlink": None // Doc("If set, specifies a symlink path to the last session log directory"),
        "last_test_symlink": None // Doc("If set, specifies a symlink path to the last test log file in each run"),
        "last_failed_symlink": None // Doc("If set, specifies a symlink path to the last failed test log file"),
        "silence_loggers": [] // Doc("Logger names to silence"),
        "format": None // Doc("Format of the log line, as passed on to logbook. None will use the default format"),
        "localtime": False // Doc("Use local time for logging. If False, will use UTC"),
    },
    "run": {
        "default_sources": [] // Doc("Default tests to run assuming no other sources are given to the runner"),
        "suite_files": [] // Doc("File(s) to be read for lists of tests to be run") // Cmdline(append="-f", metavar="FILENAME"),
        "stop_on_error": False // Doc("Stop execution when a test doesn't succeed") // Cmdline(on="-x"),
        "filter_string": None // Doc("A string filter, selecting specific tests by string matching against their name") // Cmdline(arg='-k', metavar='FILTER'),
        "repeat_each": 1 // Doc("Repeat each test a specified amount of times") // Cmdline(arg='--repeat-each', metavar="NUM_TIMES"),
        "session_state_path": "~/.slash/last_session" // Doc("Where to keep last session serialized data"),
        "project_customization_file_path": "./.slashrc",
        "user_customization_file_path": "~/.slash/slashrc",
    },
    "sentry": {
        "dsn": None // Doc("Possible DSN for a sentry service to log swallowed exceptions. "
                           "See http://getsentry.com for details"),
    },
    "plugins": {
        "search_paths": [] // Doc("List of paths in which to search for plugin modules"),
    },
})
