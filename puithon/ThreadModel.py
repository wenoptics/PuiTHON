"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date: 6/26/2019

"""
from threading import Thread, Event

import logging
logger = logging.getLogger(__name__)


class StoppableThread(Thread):
    def __init__(self, name=None):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name)
        self._evt_stop = Event()

    def run(self) -> None:
        self._evt_stop.clear()

        self._before_routine()
        while not self._evt_stop.is_set():
            self._routine()
        self._after_routine()

    def _before_routine(self):
        pass

    def _after_routine(self):
        pass

    def _routine(self):
        raise NotImplementedError()

    def stop(self):
        logging.debug(f'thread {self} stop requested')
        self._evt_stop.set()
        self.join()
        logging.debug(f'thread {self} stopped')
