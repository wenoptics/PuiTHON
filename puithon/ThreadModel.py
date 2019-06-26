from threading import Thread, Event


class StoppableThread(Thread):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)
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
        self._evt_stop.set()
        self.join()