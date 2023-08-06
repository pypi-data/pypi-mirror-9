#!/usr/bin/env python
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

import logging
from pprint import pprint

from time import sleep
from historydb import SECONDS_IN_DAY
from tests.base import BaseTestWithServers

try:
    import unittest2 as unittest
except ImportError:
    import unittest

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s:%(levelname)-8s:%(name)s:%(message)s")


class BaseAsyncTestCase(BaseTestWithServers):

    HistoryDBClient = None
    leave_files = False
    tmp_dir = "gevent-tst"

    def test_writes_and_fails(self):
        check_timeout = 1
        wait_timeout = 3
        provider_additional_kwargs = dict(check_timeout=check_timeout, wait_timeout=wait_timeout)
        n_days = 20
        stop_at = 5
        queue_size = 7
        begin_time = SECONDS_IN_DAY * 2

        user = "test_user"
        data_prefix = "test_data_"
        p = self.create_provider(**provider_additional_kwargs)
        client = self.HistoryDBClient(queue_size=queue_size, add_retries=2,
                                      **self.provider_kwargs(**provider_additional_kwargs))

        def data_gen(n):
            for i in range(n):
                yield data_prefix + str(i)

        gen_sync = data_gen(n_days)

        added_to_queue = 0
        for i in range(n_days):
            client.flush(check_timeout)
            if i >= stop_at and self.runner.is_running:
                self.runner.stop(leave_files=True)
            t = begin_time + SECONDS_IN_DAY * i
            added_to_queue += client.add_log(user, next(gen_sync), t)

        if self.runner.is_running:
            self.runner.stop(leave_files=True)

        print "added to queue", added_to_queue, client._records_queue.qsize()
        self.runner.start(self.runner.tmp_dir)
        sleep(check_timeout * 1.5)
        client.flush(check_timeout)
        end_time = begin_time + SECONDS_IN_DAY * (n_days - 1)
        logs = p.data_from_results(p.get_user_logs(user, begin_time, end_time))

        print "num logs", len(logs)
        pprint(logs)
        self.assertGreaterEqual(len(logs), stop_at)
        self.assertIn(data_prefix + "0", logs)

        data_prefix = "new_test_data"
        new_begin_time = begin_time + SECONDS_IN_DAY * (n_days + 1)
        gen_sync = data_gen(n_days)
        for i in range(n_days):
            t = new_begin_time + SECONDS_IN_DAY * i
            client.add_log(user, next(gen_sync), t)
            client.add_activity(user, t)
            client.flush()

        end_time = new_begin_time + SECONDS_IN_DAY * (n_days - 1)

        logs = p.data_from_results(p.get_user_logs(user, begin_time, end_time))
        pprint(logs)

        logs = p.data_from_results(p.get_user_logs(user, new_begin_time, end_time))
        self.assertEquals(logs, list(data_gen(n_days)))
        active_users = p.get_active_users(new_begin_time, end_time)
        self.assertIn(user, active_users)

        self.runner.stop(leave_files=True)
        client = self.HistoryDBClient(queue_size=queue_size, **self.provider_kwargs(**provider_additional_kwargs))
        new_user = "new_test_user"
        new_data = "data"
        key = "test_key"
        client.add_log_with_activity(new_user, new_data, key=key)
        self.runner.start(self.runner.tmp_dir)
        sleep(check_timeout)
        client.flush()
        self.assertEquals(p.get_active_users(keys=[key]), [new_user])
        self.assertEquals(p.data_from_results(p.get_user_logs(new_user, keys=[key])), [new_data])
