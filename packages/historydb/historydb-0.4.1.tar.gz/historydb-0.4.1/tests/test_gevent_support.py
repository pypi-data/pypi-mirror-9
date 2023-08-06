#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.abspath('..'))
from gevent.monkey import patch_all
patch_all()

from historydb.gevent_client import HistoryDBClient
from tests.base_async_test import BaseAsyncTestCase

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class HistoryDBGeventTestCase(BaseAsyncTestCase, unittest.TestCase):
    HistoryDBClient = HistoryDBClient


if __name__ == '__main__':
    unittest.main()
