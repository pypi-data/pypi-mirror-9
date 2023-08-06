from contextlib import contextmanager
from gevent import spawn, sleep, Timeout
from gevent.queue import Queue, Full, Empty
from gevent.lock import RLock
from historydb.base_client import BaseHistoryDBClient, BaseAsyncManager


class GeventAsyncManager(BaseAsyncManager):
    Queue = Queue
    RLock = RLock
    Full = Full
    Empty = Empty

    def spawn(self, func):
        return spawn(func)

    def sleep(self, seconds):
        return sleep(seconds)

    def kill(self, worker):
        worker.kill()

    @contextmanager
    def timeout(self, seconds):
        timeout = Timeout.start_new(seconds)
        try:
            yield
        except Timeout as t:
            if t is not timeout:
                raise
        finally:
            timeout.cancel()


class HistoryDBClient(BaseHistoryDBClient):
    """ HistoryDB client, which works with gevent.
    It sends records without blocking client.
    """

    async_manager = GeventAsyncManager()
