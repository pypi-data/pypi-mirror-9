# -*- coding: utf-8 -*-

from unittest2canopsis.connector import CanopsisTestResult
from unittest import TestLoader
from imp import load_source


def run_daemon(testpath, testname, amqp):
    module = load_source(testname, testpath)

    loader = TestLoader()
    suite = loader.loadTestsFromModule(module)
    result = CanopsisTestResult(module.__name__, amqp)
    suite.run(result)
    result.report()
