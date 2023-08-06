#!/usr/bin/env python
import os, sys
sys.path.insert(0, os.path.abspath('..'))
import time
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest


from tests.base import BaseTestWithServers
from historydb import ErrorNotWrittenToMinimumGroups, Provider, Error

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")


class HistoryDBFailuresTestCase(BaseTestWithServers, unittest.TestCase):

    leave_files = False

    def test_reconnect_and_silently_fail_if_not_connected(self):
        check_timeout = 1
        wait_timeout = 3
        p = self.create_provider(check_timeout=check_timeout, wait_timeout=wait_timeout)
        user = "test_user_failure"
        data = "data"
        key = "test key"
        p.add_log(user, data, key=key)

        def assertLogsEquals(excpected):
            logs = p.data_from_results(p.get_user_logs(user, keys=[key]))
            self.assertEquals(logs, excpected)

        assertLogsEquals([data])
        self.runner.stop(leave_files=True)

        with self.assertRaises(ErrorNotWrittenToMinimumGroups):
            p.add_log(user, data, key=key)

        r = p.add_log_async(user, data, key=key)
        r.wait()
        self.assertFalse(r.successful())

        assertLogsEquals([])

        self.runner.start(self.runner.tmp_dir)
        time.sleep(check_timeout * 1.5)
        assertLogsEquals([data])
        p = self.create_provider()
        assertLogsEquals([data])

    @unittest.skip("Segmentation fault")
    def test_cant_connect_to_some_nodes(self):
        bad_addr = "bad_host:1026:2"
        p = Provider([self.elliptics_addr, bad_addr], [1])
        s = p.create_session()
        self.assertTrue(len(s.get_routes()))

        with self.assertRaises(Error):
            Provider([bad_addr], [1])


if __name__ == '__main__':
    unittest.main()
