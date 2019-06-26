from collections import defaultdict
from functools import partial
from queue import Queue

from cefpython3 import cefpython as cef

from puithon.ThreadModel import StoppableThread

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


class BindFunctionThread(StoppableThread):

    def __init__(self):
        super().__init__()
        self.q_function = Queue()

    def _routine(self):
        browser, jsname, pyhandler, = self.q_function.get()
        global_js_bindings[browser].SetFunction(jsname, pyhandler)
        browser.SetJavascriptBindings(global_js_bindings[browser])

    def add_js_binding(self, browser, js_name, py_handler):
        self.q_function.put((browser, js_name, py_handler))


class JavascriptReturnThread(StoppableThread):

    def __init__(self):
        super().__init__()
        self.q_value = Queue()

        # a waiting queue map (key is 'what') for massage consuming
        self.q_dict_waiting = defaultdict(Queue)

    def _routine(self):
        what, value = self.q_value.get()
        # Dispatch the value message
        self.q_dict_waiting[what].put(value)

    def put_value(self, what, value):
        """
        Typically, this is called from Javascript (the js engine)
        :param what:
        :param value:
        :return:
        """
        self.q_value.put((what, value))

    def wait_for_value(self, what):
        """
        Block and wait for value

        :param what:
        :return:
        """
        return self.q_dict_waiting[what].get()

    def subscribe(self, browser):
        """
        Subscribe for javascript returned values

        :param browser:
        :return:
        """
        bind_setting.add_js_binding(browser, 'pyJsReturnPut', self.put_value)


bind_setting = BindFunctionThread()
bind_setting.start()
jsreturned = JavascriptReturnThread()
jsreturned.start()
