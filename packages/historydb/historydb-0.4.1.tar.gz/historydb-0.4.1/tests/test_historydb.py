#!/usr/bin/env python
import os, sys
sys.path.insert(0, os.path.abspath('..'))
import time
import logging
import random
from datetime import timedelta

try:
    import unittest2 as unittest
except ImportError:
    import unittest


from historydb import Provider, SECONDS_IN_DAY
from tests.base import BaseTestWithServers

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")


class HistoryDBTestCase(BaseTestWithServers, unittest.TestCase):

    def test_add_read_logs_and_activities(self):
        n_days = 10
        begin_time = time.time()
        end_time = begin_time + SECONDS_IN_DAY * (n_days - 1)
        user = "test_user"
        async_user = "test_user_async"
        data = "test_data_"
        p = Provider([self.elliptics_addr], [1])

        def data_gen(n):
            for i in range(n):
                yield data + str(i)

        gen_sync = data_gen(n_days)
        gen_async = data_gen(n_days)

        async_results = []
        for i in range(n_days):
            t = begin_time + SECONDS_IN_DAY * i
            p.add_log(user, next(gen_sync), t)
            async_results.append(p.add_log_async(async_user, next(gen_async), t))
            p.add_activity(user, t)
            async_results.append(p.add_activity_async(async_user, t))

        p.wait(async_results)
        logs = p.data_from_results(p.get_user_logs(user, begin_time, end_time))
        self.assertEquals(len(logs), n_days)

        logs = p.data_from_results(p.iter_user_logs(async_user, begin_time, end_time))
        self.assertEquals(len(logs), n_days)
        self.assertEquals(logs, list(data_gen(n_days)))

        active_users = p.get_active_users(begin_time, end_time)
        self.assertIn(user, active_users)
        self.assertIn(async_user, active_users)

    def test_different_resolution_at_the_same_time(self):
        n_logs = 10
        seconds_in_minute = 60
        seconds_in_hour = seconds_in_minute * 60
        begin_time = time.time()
        user_hourly = "test_user_hourly"
        user_minutes = "test_user_minutes"
        data_hourly = "hourly\n"
        data_minutes = "minutes\n"
        p_hourly = Provider([self.elliptics_addr], [1], key_resolution=seconds_in_hour)
        p_minutes = Provider([self.elliptics_addr], [1], key_resolution=seconds_in_minute)
        for i in range(n_logs):
            p_hourly.add_log(user_hourly, data_hourly, begin_time + seconds_in_hour * i)
            p_minutes.add_log(user_minutes, data_minutes, begin_time + seconds_in_minute * i)

        logs = p_hourly.data_from_results(p_hourly.get_user_logs(user_hourly, begin_time,
                                                                 begin_time + seconds_in_hour * (n_logs - 1)))
        self.assertEquals(len(logs), n_logs)
        self.assertEquals(logs, [data_hourly] * n_logs)

        logs = p_minutes.data_from_results(p_minutes.get_user_logs(user_minutes, begin_time,
                                                                   begin_time + seconds_in_minute * (n_logs - 1)))
        self.assertEquals(len(logs), n_logs)
        self.assertEquals(logs, [data_minutes] * n_logs)

    @unittest.skip("Segmentation fault. Probably in get_active_users()")
    def test_logs_with_activities(self):
        n_days = 10
        begin_time = time.time()
        end_time = begin_time + SECONDS_IN_DAY * (n_days - 1)
        p = Provider([self.elliptics_addr], [1])
        user = "test_user_with_activity"
        data = "test_data\n"
        for i in range(n_days):
            p.add_log_with_activity(user, data, begin_time + SECONDS_IN_DAY * i)

        logs = p.data_from_results(p.get_user_logs(user, begin_time, end_time))
        self.assertEquals(len(logs), n_days)

        self.assertEquals(logs, [data] * n_days)
        active_users = p.get_active_users(begin_time, end_time)
        self.assertIn(user, active_users)

    def test_keys_instead_time(self):
        p = Provider([self.elliptics_addr], [1])
        user = "test_user_for_keys"
        key1 = "key1"
        key2 = "key2"
        keys = [key1, key2]
        p.add_log(user, key1, key=key1)
        p.add_log(user, key2, key=key2)
        data = p.data_from_results(p.get_user_logs(user, keys=keys))
        self.assertEquals(data, keys)

    def test_key_or_time_not_specified(self):
        p = Provider([self.elliptics_addr], [1])
        user = "test_user_without_args"
        data = "data"
        p.add_log(user, data)
        logs = p.data_from_results(p.get_user_logs(user, time.time()))
        self.assertEquals(logs, [data])

    def test_remove_old_logs(self):
        p = Provider([self.elliptics_addr], [1])

        data = "data"
        start_ts = time.time() - timedelta(days=365 * 3).total_seconds()
        ts = start_ts
        n = 10

        for i in range(n):
            user = "test_remove_old_logs %s" % random.randint(0, 9999999)
            p.add_log_with_activity(user, data, time=ts)
            ts -= p.key_resolution

        self.assertEquals(p.remove_old_logs(start_ts), n)


if __name__ == '__main__':
    unittest.main()
