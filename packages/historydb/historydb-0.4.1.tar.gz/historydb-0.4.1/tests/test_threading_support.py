#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from historydb.threading_client import HistoryDBClient
from tests.base_async_test import BaseAsyncTestCase

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class HistoryDBThreadingTestCase(BaseAsyncTestCase, unittest.TestCase):
    HistoryDBClient = HistoryDBClient


if __name__ == '__main__':
    unittest.main()
