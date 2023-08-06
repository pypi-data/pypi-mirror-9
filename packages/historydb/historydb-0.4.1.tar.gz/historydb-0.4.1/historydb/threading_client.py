from Queue import Queue, Full, Empty
from threading import RLock, Thread
from time import sleep
from historydb.base_client import BaseHistoryDBClient, BaseAsyncManager


class ThreadingAsyncManager(BaseAsyncManager):
    Queue = Queue
    RLock = lambda *a: RLock()  # This is needed because threading.RLock is a function, not a class
    Full = Full
    Empty = Empty

    def spawn(self, func):
        t = Thread(target=func)
        t.daemon = True
        t.start()
        return t

    def sleep(self, seconds):
        return sleep(seconds)

    def kill(self, worker):
        pass


class HistoryDBClient(BaseHistoryDBClient):
    """ HistoryDB client, which works with threading.
    It sends records without blocking client.
    """

    async_manager = ThreadingAsyncManager()

    def flush(self, timeout=None):
        # it's little hacky, because thread not really interrupted
        t = self.async_manager.spawn(self._do_flush)
        t.join(timeout)
