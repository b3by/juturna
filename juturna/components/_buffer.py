import threading
import collections

from juturna.components import Message
from juturna.utils.log_utils import jt_logger


class Buffer:
    def __init__(self, creator: str):
        self._data: dict[str, collections.deque[Message]] = dict()
        self._data_lock = threading.Lock()
        self._creator = creator
        self._logger = jt_logger(creator)
        self._logger.propagate = True

    def append_data(self, message: Message):
        if message.creator not in self._data:
            self._data[message.creator] = collections.deque()

        with self._data_lock:
            self._data[message.creator].append(message)

    def flush(self):
        with self._data_lock:
            self._data = dict()

    def drain(self): ...
