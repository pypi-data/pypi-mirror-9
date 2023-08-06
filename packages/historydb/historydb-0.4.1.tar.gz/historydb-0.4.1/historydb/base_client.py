import logging
from collections import namedtuple, deque

from .provider import Provider, ConnectionError, Error


DEFAULT_POOL_TIMEOUT = 0.01
log = logging.getLogger("historydb_client")


class BaseAsyncManager(object):
    Queue = None
    RLock = None
    Full = None
    Empty = None

    def spawn(self, func):
        return NotImplemented

    def sleep(self, seconds):
        return NotImplemented

    def kill(self, worker):
        return NotImplemented

    def timeout(self, seconds):
        return NotImplemented


class BaseHistoryDBClient(object):
    """ HistoryDB client, which works with gevent.
    It sends records without blocking client.
    """

    provider_class = Provider
    async_manager = BaseAsyncManager()

    def __init__(self,
                 queue_size=100, simultaneous_writes=10,
                 connection_retries=1, add_retries=5,
                 add_timeout=0.02, reconnect_timeout=3,
                 pool_timeout=DEFAULT_POOL_TIMEOUT,
                 **provider_kwargs):
        """

        :param queue_size: How many records can be queued
        :param simultaneous_writes: Number of simultaneous writes
        :param connection_retries: Provider connection retries
        :param add_retries: How many times we will try to resend record
        :param add_timeout: Timeout for add_log* operations. It will wait for this time if queue is full
        :param reconnect_timeout: Wait this time before next reconnect
        :param pool_timeout: Used for pooling when waiting for result fro elliptics
        :param provider_kwargs: Keyword arguments for :class:`historydb.Provider`
        """
        self.add_timeout = add_timeout
        self.connection_retries = connection_retries
        self.reconnect_timeout = reconnect_timeout
        self.pool_timeout = pool_timeout
        self.provider_kwargs = provider_kwargs

        self._provider = None
        self._min_writes = None
        self._simultaneous_writes = simultaneous_writes
        self._max_record_retries = add_retries
        self._records_queue = self.async_manager.Queue(queue_size)
        self._results = deque(maxlen=simultaneous_writes)
        self._result_lock = self.async_manager.RLock()
        self.background_worker = self.async_manager.spawn(self._worker_loop)

    def __del__(self):
        self.async_manager.kill(self.background_worker)

    def add_log(self, user, data, time=None, key=None):
        return self._put(LogRecord(user, data, time, key))

    def add_activity(self, user, time=None, key=None):
        return self._put(ActivityRecord(user, time, key))

    def add_log_with_activity(self, user, data, time=None, key=None):
        return self._put(LogWithActivityRecord(user, data, time, key))

    def flush(self, timeout=None):
        """ Flushes all messages
        :param timeout: Maximum time to wait. Note: it can be longer than this parameter if something blocks gevent.
        """
        log.info("Flush records, timeout = %s", timeout)
        with self.async_manager.timeout(timeout):
            self._do_flush()

    def _do_flush(self):
        while True:
            try:
                retries, record = self._records_queue.get_nowait()
            except self.async_manager.Empty:
                break
            self._handle_record(record, retries)
        self._wait_all_writes()

    def join(self, timeout=None):
        """ Join background worker. You don't really need this.
        :param timeout:
        :return:
        """
        self.background_worker.join(timeout)

    def _put(self, record, priority=0):
        try:
            self._records_queue.put((priority, record), timeout=self.add_timeout)
        except self.async_manager.Full:
            log.warning("Add record failed, queue is full")
            return False
        return True

    def _worker_loop(self):
        log.info("Worker started")
        while True:
            retries, record = self._records_queue.get()
            try:
                self._handle_record(record, retries)
            except Exception:
                log.exception("Exception while handling record")

    def _handle_record(self, record, retries=0):
        try:
            provider = self.get_provider()
            result = record.send(provider)
        except Error as e:
            log.error("Send failed due to error %r", e)
            result = None
        with self._result_lock:
            self._results.append(RecordWithResult(record, result, retries))
        if len(self._results) >= self._simultaneous_writes:
            self._wait_all_writes()

    def _wait_all_writes(self):
        if not self._results:
            return
        log.debug("Begin waiting for %s", self._results)

        with self._result_lock:
            results = list(self._results)
            self._results.clear()
        for r in results:
            if r.wait_writes(self.pool_timeout, self.async_manager.sleep) < self._min_writes:
                if r.retries < self._max_record_retries:
                    log.info("Failed to write %r, retrying it. %s retries so far", r.record, r.retries)
                    self._put(r.record, r.retries + 1)
                else:
                    log.error("Failed to write %r, %s times", r.record, r.retries)

    def get_provider(self):
        """
        Mostly internal.
        Tries to connect to elliptics nodes.

        If connection failed :attr:`connection_retries` times, it will raise :class:`ConnectionError`

        :return: :class:`historydb.Provider`
        """
        if self._provider is None:
            retries = self.connection_retries
            while True:
                try:
                    self._provider = self.provider_class(**self.provider_kwargs)
                    self._min_writes = self._provider.min_writes
                    break
                except ConnectionError:
                    if not retries:
                        raise
                    log.warning("Provider connection error, retries left: %s", retries)
                    retries -= 1
                    self.async_manager.sleep(self.reconnect_timeout)
        return self._provider


class LogReprMixin(object):
    def __repr__(self):
        limit = 256
        data = self.data
        if len(data) > limit:
            data = data[:limit] + "..."
        return "%s(%r, %r, %r, %r)" % (self.__class__.__name__, self.user, data, self.time, self.key)

    __str__ = __repr__


class LogRecord(namedtuple("LogRecord", "user data time key"), LogReprMixin):

    def send(self, provider):
        return provider.add_log_async(*self)


class ActivityRecord(namedtuple("ActivityRecord", "user time key")):
    def send(self, provider):
        return provider.add_activity_async(*self)


class LogWithActivityRecord(namedtuple("LogWithActivityRecord", "user data time key"), LogReprMixin):
    def send(self, provider):
        log_result = provider.add_log_async(*self)
        provider.add_activity_async(self.user, self.time, self.key)
        return log_result


class RecordWithResult(namedtuple("RecordWithResult", "record result retries")):
    def wait_writes(self, pool_timeout=DEFAULT_POOL_TIMEOUT, sleep=None):
        r = self.result
        if r is None:
            return 0

        while not r.ready():
            sleep(pool_timeout)
        return len(r.get())
