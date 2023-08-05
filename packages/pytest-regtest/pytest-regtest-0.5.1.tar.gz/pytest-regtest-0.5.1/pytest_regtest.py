# encoding: utf-8

"""Regresstion test plugin for pytest.

This plugin enables recording of ouput of testfunctions which can be compared on subsequent
runs.
"""

import cStringIO
import contextlib
import difflib
import os
import sys

import pytest


def pytest_addoption(parser):
    """Add options to control the timeout plugin"""
    group = parser.getgroup('regtest', 'regression test plugin')
    group.addoption('--regtest-reset',
                    action="store_true",
                    help="do not run regtest but record current output")
    group.addoption('--regtest-nodiff',
                    action="store_true",
                    default=False,
                    help="suppress out put of diff in error report")
    group.addoption('--regtest-tee',
                    action="store_true",
                    default=False,
                    help="print recorded results to console too")


recorded_diffs = dict()
failed_tests = set()
no_diff = False
tee = False


def pytest_configure(config):
    recorded_diffs.clear()
    failed_tests.clear()
    global no_diff, tee
    no_diff = False
    tee = False


def _finalize(fp, request):

    reset, full_path, id_ = _setup(request)
    if reset:
        _record_output(fp.getvalue(), full_path)
    else:
        _compare_output(fp.getvalue(), full_path, request, id_)


class Tee(object):

    def __init__(self, string_io):
        self.string_io = string_io

    def write(self, data):
        self.string_io.write(data)
        sys.__stdout__.write(data)

    def __getattr__(self, name):
        return getattr(self.string_io, name)


@pytest.yield_fixture()
def regtest(request):

    fp = cStringIO.StringIO()
    if tee:
        fp = Tee(fp)

    yield fp

    _finalize(fp, request)


@pytest.yield_fixture()
def regtest_redirect(request):

    fp = cStringIO.StringIO()
    if tee:
        fp = Tee(fp)

    @contextlib.contextmanager
    def context(fp=fp):
        import sys
        old = sys.stdout
        sys.stdout = fp
        yield
        sys.stdout = old

    yield context

    _finalize(fp, request)


"""

# THIS DOES NOT WORK AS INTENDED BECAUSE OF py.tests INTERNAL REDIRECTION !
# I LEAVE THIS SNIPPET HERE TO AVOID ANOTHER UNSUCCUESSFULL IMPLEMENTATION IN THE FUTURE.

@pytest.yield_fixture()
def regtest_capture_all(request):

    fp = cStringIO.StringIO()

    import sys
    old = sys.stdout
    sys.stdout = fp

    try:
        yield
    finally:
        sys.stdout = old

    _finalize(fp, request)

"""


def pytest_report_teststatus(report):
    if report.when == "call":
        if report.outcome == "failed":
            failed_tests.add(report.nodeid)
    if report.when == "teardown":
        msg = recorded_diffs.get(report.nodeid, "")
        if report.outcome == "passed":
            if msg and report.nodeid not in failed_tests:
                return "rfailed", "R", "Regression test failed"


def pytest_terminal_summary(terminalreporter):
    tr = terminalreporter
    first = True
    if no_diff:
        return
    for nodeid, msg in sorted(recorded_diffs.items()):
        if msg and nodeid not in failed_tests:
            if first:
                tr._tw.line()
            first = False
            tr._tw.sep(".", " %s rfailed because recorded output differs as follows " % nodeid)
            tr._tw.line()
            tr._tw.line(msg)


def _setup(request):

    global no_diff, tee
    no_diff = request.config.getoption("--regtest-nodiff")
    tee = request.config.getoption("--regtest-tee")
    reset = request.config.getoption("--regtest-reset")
    path = request.fspath.strpath
    func_name = request.function.__name__
    dirname = os.path.dirname(path)
    basename = os.path.basename(path)
    stem, ext = os.path.splitext(basename)

    target_dir = os.path.join(dirname, "_regtest_outputs")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    id_ = "%s.%s" % (stem, func_name)
    full_path = os.path.join(target_dir, "%s.out" % (id_))
    return reset, full_path, id_


def _compare_output(is_, path, request, id_):
    capman = request.config.pluginmanager.getplugin('capturemanager')
    if capman:
        stdout, stderr = capman.suspendcapture(request)
    else:
        stdout, stderr = None, None
    if os.path.exists(path):
        with open(path, "r") as fp:
            tobe = fp.read()
    else:
        tobe = ""
    __tracebackhide__ = True
    collected = list(difflib.unified_diff(is_.split("\n"), tobe.split("\n"), "is", "to", lineterm=""))
    if collected:
        recorded_diffs[request.node.nodeid] = "\n".join(collected)
    else:
        recorded_diffs[request.node.nodeid] = ""


def _record_output(is_, path):
    with open(path, "w") as fp:
        fp.write(is_)
