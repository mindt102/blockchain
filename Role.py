import queue
import threading

import utils


class Role(threading.Thread):
    __logger = utils.get_logger(__name__)
    __run_event = threading.Event()

    def __init__(self):  # type: ignore
        self.q = queue.Queue()
        self.q_timeout = 1.0/60

        if not self.active():
            self.__run_event.set()
        super().__init__()

    def _rpc(func):  # type: ignore
        def wrapper(self, *args, **kwargs):
            self.q.put((func, (self, *args), kwargs))
        return wrapper

    def active(self):
        return self.__run_event.is_set()

    @classmethod
    def deactivate(cls):
        cls.__run_event.clear()
