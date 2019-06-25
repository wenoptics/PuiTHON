from collections import defaultdict
from functools import partial
from queue import Queue
from threading import Thread, Event

from cefpython3 import cefpython as cef

_py_callbacks_ = {}
global_js_bindings = defaultdict(partial(
    cef.JavascriptBindings, {'bindToFrames': False, 'bindToPopups': False})
)


def get_python_callback_js_name(obj):
    """
    Utility function

    :param obj:
    :return:
    """
    return f'_py_callbacks__{obj.__name__}_{hex(id(obj))}'


class BindingSettingThread(Thread):
    def __init__(self):
        super().__init__()
        self.q = Queue()
        self._evt_stop = Event()

    def run(self):
        while not self._evt_stop.is_set():
            browser, jsname, pyhandler, = self.q.get()
            global_js_bindings[browser].SetFunction(jsname, pyhandler)
            browser.SetJavascriptBindings(global_js_bindings[browser])

    def stop(self):
        self._evt_stop.set()
        self.join()

    def add_js_binding(self, browser, js_name, py_handler):
        self.q.put((browser, js_name, py_handler))


bind_setting = BindingSettingThread()
bind_setting.start()
