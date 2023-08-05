""" goulash.stdout

    (used by corkscrew.comet)
"""

import sys
import threading
from Queue import Queue, Empty

class ThreadedStdout(object): # pragma: no-cover
    """ Replacement for sys.stdout where every thread gets it's own
        queue.  Useful for capturing printed output from functions
        that are run in threads.  This is a toy, and not really a
        great idea to use except in short-lived programs.  See usage
        in corkscrew.comet
    """
    def __init__(self, stdout=None):
        self.stdout = stdout if stdout is not None else sys.stdout
        self.registry = {}

    def install(self):
        if sys.stdout != self:
            sys.stdout = self

    def __getattr__(self, x):
        return getattr(self.stdout, x)

    def register(self, thread):
        q = Queue()
        self.registry[thread] = q
        return q

    def read_all(self, thread):
        result = ""
        q = self.registry[thread]
        while q.qsize():
            try:
                result += q.get(block=False)
            except Empty:
                pass
        return result

    def write(self, data):
        this = threading.current_thread()
        if this in self.registry:
            self.registry[this].put(data)
        else:
            self.stdout.write(data)
