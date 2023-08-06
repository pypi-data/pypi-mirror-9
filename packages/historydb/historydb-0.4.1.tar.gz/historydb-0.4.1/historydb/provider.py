#!/usr/bin/env python
import os
import logging
import socket
from time import time as now

import elliptics
from elliptics import Address
from elliptics.core import exceptions_policy, log_level as LogLevel, Error


SECONDS_IN_DAY = 24 * 60 * 60


# Monkey-patch elliptics.Address.log, until it's fixed at github
Address.log = logging.getLogger("elliptics.Address")


class ErrorNotWrittenToMinimumGroups(Error):
    """ Raised if data wasn't written to minimum nubmer of groups
    """
    pass


class ConnectionError(Error):
    """ Failed to connect to at least one server
    """
    pass


class Provider(object):
    """ HistoryDb client
    """

    def __init__(self, servers, groups, min_writes=None,
                 wait_timeout=5, check_timeout=60,
                 key_resolution=SECONDS_IN_DAY,
                 log_file=os.devnull, log_level=LogLevel.info,
                 enable_exceptions=False):
        """

        :param servers: List of Elliptics servers, e.g. ["host1:1025:2", "host2:1025:2"]
        :param groups: List of groups, with which HistoryDB will work, e.g. [1, 2]
        :param min_writes: For each write attempt some group or groups could fail write.
                           `min_writes` - minimum numbers of groups which shouldn't fail write.
                           default - number of groups
        :param wait_timeout: Session's `wait_timeout`. This timeout affects all transactions
                             that we send to the cluster. Default is 5 seconds.
        :param check_timeout: Session's `check_timeout`. A separate thread which scans for timed out transactions,
                              it also ensures that we update the routing table and checks the network connection
                              (for example, that we have not timed out). By default - 60 seconds.
        :param key_resolution: Resolution of keys, default `SECONDS_IN_DAY`
        :param log_file: Path to log file, default "/dev/null"
        :param log_level: Log level, default `info`
        :param enable_exceptions: If `True`, elliptics will raise exceptions, default `False`
        """
        self._servers = servers
        self._groups = groups

        if min_writes is None:
            min_writes = len(groups)
        self.key_resolution = key_resolution
        self.min_writes = min(min_writes, len(groups))
        self.enable_exceptions = enable_exceptions

        self._log = elliptics.Logger(log_file, log_level)
        self._cfg = elliptics.Config()
        self._cfg.config.wait_timeout = wait_timeout
        self._cfg.config.check_timeout = check_timeout
        self._node = elliptics.Node(self._log, self._cfg)
        self._connect()

    def create_session(self, io_flags=0):
        """ Create session with proper config and passed `io_flags`.

        Mainly used internally, but you can use it when some low level operations needed
        :return: Ellitptics.Session instance
        """
        ret = elliptics.Session(self._node)
        ret.set_ioflags(io_flags)
        ret.set_cflags(0)
        ret.set_groups(self._groups)
        if not self.enable_exceptions:
            ret.set_exceptions_policy(exceptions_policy.no_exceptions)
        return ret

    def _connect(self):
        for serv in self._servers:
            try:
                addr = Address.from_host_port_family(serv)
                self._node.add_remote(addr.host, addr.port, addr.family)
            except (socket.gaierror, socket.error, Error):
                pass
        s = self.create_session()
        if not s.get_routes():
            raise ConnectionError("Failed to connect to at least one server")

    def add_log(self, user, data, time=None, key=None):
        """ Add (append) data to user logs
        :param user: Name of user, or it's ID
        :param data: log data
        :param time: timestamp of the log record
        :param key: custom key for log record

        You can pass either `timestamp` or `key`, if both is specified, key will be used.
        If nothing specified, log will be recorded with current system timestamp

        :raises: ErrorNotWrittenToMinimumGroups
        """
        r = self.add_log_async(user, data, time, key)
        self._assert_data_written(r)

    def add_log_async(self, user, data, time=None, key=None):
        """ Same as :meth:`add_log`, but adds log asynchronously.

        :returns: `Elliptics.AsyncResult`
        """
        session = self.create_session(elliptics.io_flags.append)
        key = combine_key(user, self._time_or_key_to_key(time, key))
        return session.write_data(key, data)

    def add_activity(self, user, time=None, key=None):
        """ Adds user to activity statistics
        It's need if you need to find some active users later
        :param user: Name or id of user
        :param time: Timestamp
        :param key: Custom key
        :return: None

        You can pass either `timestamp` or `key`, if both is specified, key will be used.
        If nothing specified, activity will be recorded with current system timestamp

        :raises: ErrorNotWrittenToMinimumGroups
        """
        r = self.add_activity_async(user, time, key)
        self._assert_data_written(r)

    def add_activity_async(self, user, time=None, key=None):
        """ Same as :meth:`add_activity`, but works asynchronously.

        :returns: `Elliptics.AsyncResult`
        """
        session = self.create_session()
        key = self._time_or_key_to_key(time, key)
        return session.update_indexes_internal(combine_key(user, key), [key], [user])

    def add_log_with_activity(self, user, data, time=None, key=None):
        """ Adds data to user logs and user to activity statistics

        Parameters are same as in :meth:`add_log`

        :raises: ErrorNotWrittenToMinimumGroups
        """
        key = self._time_or_key_to_key(time, key)
        log_result = self.add_log_async(user, data, key=key)
        act_result = self.add_activity_async(user, key=key)
        self._assert_data_written(log_result)
        self._assert_data_written(act_result)

    def get_user_logs(self, user, begin_time=None, end_time=None, keys=None):
        """ Returns user's logs for specified period or list of keys
        :param user: Name of user
        :param begin_time: begin of the time period (timestamp)
        :param end_time: end of the time period (timestamp)
        :param keys: custom keys
        :return: list of `elliptics.ReadResultEntry`

        You can pass either `begin_time` and `end_time` or keys. If both specified, the `keys` will be used.
        Also, you can specify only `begin_time`, then `end_time` will be equal to current system time

        ``ReadResultEntry`` contains following fields:
            id: Id
            data: string with stored data
            address:
            timestamp: elliptics Time (now, tsec, tnsec)

            size: size of data
            offset: offset of data
            error: code, message
        """
        return list(self.iter_user_logs(user, begin_time, end_time, keys))

    def iter_user_logs(self, user, begin_time=None, end_time=None, keys=None):
        """ Same as :meth:`get_user_logs` but returns iterator instead list
        """
        session = self.create_session()
        if not keys:
            assert begin_time is not None, "You must specify keys or begin_time"
            keys = self.time_period_to_subkeys(begin_time, end_time)
        # start all requests at once
        results = [session.read_latest(combine_key(user, key))
                   for key in keys]
        for r in results:
            entry = r.get()
            if entry and r.successful():
                yield entry[0]

    def get_active_users(self, begin_time=None, end_time=None, keys=None):
        """ Gets active users with activity statistics for specified period
        :param begin_time: begin of the time period (timestamp)
        :param end_time: end of the time period (timestamp)
        :param keys: list of custom keys
        :return: list of user's names

        You can pass either `begin_time` and `end_time` or keys. If both specified, the `keys` will be used.
        Also, you can specify only `begin_time`, then `end_time` will be equal to current system time
        """
        return list(self.iter_active_users(begin_time, end_time, keys))

    def iter_active_users(self, begin_time=None, end_time=None, keys=None):
        """ Same as :meth:`get_active_users` but returns iterator instead list
        """
        session = self.create_session()
        if not keys:
            keys = self.time_period_to_subkeys(begin_time, end_time)
        result = session.find_any_indexes(keys)
        seen = set()
        for res in result.get():
            for idx in res.indexes:
                data = idx.data
                if data not in seen:
                    yield data
                    seen.add(data)

    @staticmethod
    def wait(async_results):
        """ Wait for all `elliptics.AsyncResult` s
        :param async_results: iterable of `elliptics.AsyncResult`
        """
        for r in async_results:
            r.wait()

    def iter_data_from_results(self, results):
        """ Iterates `elliptics.ResultEntry` and yields data for result

        :param results: iterable of `elliptics.ResultEntry`
        """
        for r in results:
            try:
                yield r.data
            except Error:
                pass

    def data_from_results(self, results):
        """ Returns list of data from iterable of `elliptics.ResultEntry` s

        :param results: iterable of `elliptics.ResultEntry`
        """
        return list(self.iter_data_from_results(results))

    def time_to_subkey(self, t):
        return str(int(t) // self.key_resolution)

    def time_period_to_subkeys(self, begin_time, end_time=None):
        begin = int(begin_time) // self.key_resolution
        end = int(end_time or begin_time) // self.key_resolution
        return map(str, xrange(begin, end + 1))

    def remove_old_logs(self, older_than_time, minimum_time=0, allowed_gap=60):
        session = self.create_session()
        assert isinstance(session, elliptics.Session)
        assert isinstance(self, Provider)
        deleted_entries = 0
        empty_intervals = 0

        for cur_time in range(int(older_than_time), int(minimum_time), -self.key_resolution):
            key = self.time_to_subkey(cur_time)
            users = self.get_active_users(keys=[key])
            if not users:
                empty_intervals += 1
                if empty_intervals > allowed_gap:
                    break
                continue
            else:
                empty_intervals = 0

            for user in users:
                entry_key = combine_key(user, key)
                r1 = session.set_indexes(entry_key, [], [])
                r2 = session.remove(entry_key)
                self.wait([r1, r2])
            deleted_entries += 1

        return deleted_entries

    def _time_or_key_to_key(self, time, key):
        if key is None:
            if time is None:
                time = now()
            key = self.time_to_subkey(time)
        return key

    def _assert_data_written(self, result):
        if len(result.get()) < self.min_writes:
            raise ErrorNotWrittenToMinimumGroups(
                "Data wasn't written to minimum number of groups"
            )


def combine_key(*parts):
    return '.'.join(parts)


def time_to_etime(t):
    seconds = int(t)
    nseconds = int((t - seconds) * 1000000000)
    return elliptics.Time(seconds, nseconds)


def etime_to_time(ts):
    return ts.tsec + ts.tnsec / 1000000000.0
