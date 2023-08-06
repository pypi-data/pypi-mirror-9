import datetime
import socket
import sys
from ..interface import PluginInterface
from ...ctx import context
from ...utils.traceback_utils import get_traceback_string
from ...utils.conf_utils import Cmdline
from slash import config as slash_config
from xml.etree.ElementTree import (
    tostring as xml_to_string,
    Element as E,
    )

class Plugin(PluginInterface):

    def get_name(self):
        return "xunit"

    def activate(self):
        slash_config["plugins"].extend({"xunit": {"filename": "testsuite.xml" // Cmdline(arg="--xunit-filename")}})

    def deactivate(self):
        slash_config["plugins"].pop("xunit")

    def session_start(self):
        self._start_time = datetime.datetime.now()
        self._xunit_elements = []

    def test_start(self):
        self._xunit_elements.append(E("testcase", {
            "name": str(context.test),
            "classname": type(context.test).__name__,
            "time": "0"
        }))

    def test_success(self):
        pass

    def test_error(self):
        self._add_error("error")

    def test_failure(self):
        self._add_error("failure")

    def _add_error(self, errortype):
        exc_type, exc_value, exc_tb = exc_info = sys.exc_info()
        test_element = self._xunit_elements[-1]
        error_element = E(errortype, dict(type=exc_type.__name__, message=str(exc_value)))
        error_element.text = get_traceback_string(exc_info)
        test_element.append(error_element)

    def _get_test_case_element(self, test):
        return E('testcase', dict(name=str(test), classname="{}.{}".format(test.__class__.__module__, test.__class__.__name__), time="0"))

    def test_skip(self, reason):
        test_element = self._xunit_elements[-1]
        test_element.append(E('skipped', type=reason))

    def result_summary(self):
        e = E('testsuite', {
            "name": "slash-suite",
            "hostname": socket.getfqdn(),
            "timestamp": self._start_time.isoformat().rsplit(".", 1)[0],
            "time": "0",
            "tests": str(context.session.results.get_num_results()),
            "errors": str(context.session.results.get_num_errors()),
            "failures": str(context.session.results.get_num_failures()),
            "skipped": str(context.session.results.get_num_skipped()),
        })
        for element in self._xunit_elements:
            e.append(element)
        with open(slash_config.root.plugins.xunit.filename, "wb") as outfile:
            outfile.write(xml_to_string(e))
