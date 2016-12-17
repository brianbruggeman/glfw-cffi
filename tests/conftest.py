# -*- coding: utf-8 -*-
from fixtures import *  # noqa


def pytest_addoption(parser):
    parser.addoption("--stress", action="store_true", help="run stress tests")
    parser.addoption("--license", action="store_true", help="run license tests")
    parser.addoption("--long-running", action="store_true", help="run slow tests")
