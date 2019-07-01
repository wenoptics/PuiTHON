"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date:

"""
import queue
import threading
from collections import defaultdict
from functools import partial
from queue import Queue
import platform
import sys
import ctypes
from threading import Event

from cefpython3 import cefpython as cef

from puithon.ThreadModel import StoppableThread

import logging
logger = logging.getLogger(__name__)

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


class _BindFunctionThread(StoppableThread):

    def __init__(self):
        super().__init__()
        self.q_function = Queue()

    def _routine(self):
        try:
            browser, jsname, pyhandler, = self.q_function.get_nowait()
        except queue.Empty:
            pass
        else:
            global_js_bindings[browser].SetFunction(jsname, pyhandler)
            browser.SetJavascriptBindings(global_js_bindings[browser])

    def add_js_binding(self, browser, js_name, py_handler):
        self.q_function.put((browser, js_name, py_handler))


class _JavascriptReturnThread(StoppableThread):
    """
    On Javascript side (the js-engine), values will be pushed here
    (CEFPython does not allow instant javascript returns)

    """

    def __init__(self):
        super().__init__()
        self.q_value = Queue()

        # a waiting queue map (key is 'what') for massage consuming
        self.q_dict_waiting = defaultdict(Queue)

    def _routine(self):
        try:
            what, value = self.q_value.get_nowait()
        except queue.Empty:
            pass
        else:
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

    def on_value(self, what, handler):
        """
        Asynchronous approach the get called on value

        :param what:
        :param handler:
        :return:
        """
        from threading import Thread
        Thread(target=lambda: handler(self.wait_for_value(what)),
               name=f'{self.__class__.__name__}->on_value')\
            .start()

        # fixme This thread will be leaked and run forever if no value received

    def subscribe(self, browser):
        """
        Subscribe for javascript returned values

        :param browser:
        :return:
        """
        RuntimeManager.get_instance().FunctionBinding.add_js_binding(browser, 'pyJsReturnPut', self.put_value)


class _WindowManaging:
    """
    WindowManaging for window manage purpose. This is the UI Thread. Should be run on the main thread.

    todo Make this a singleton

    """

    class WindowManager:

        def __init__(self):
            self.list_windows = []

        class _CEFLoadHandler:
            def __init__(self, on_dom_ready=None, on_before_close=None):
                self._on_before_close = on_before_close
                self._on_dom_ready = on_dom_ready

            def OnLoadingStateChange(self, browser, is_loading, **_):
                """Called when the loading state has changed."""
                logging.debug(f'OnLoadingStateChange, {browser}')
                if not is_loading:
                    # Loading is complete. DOM is ready.
                    if self._on_dom_ready is not None:
                        self._on_dom_ready()

            def OnBeforeClose(self, browser):
                logging.debug(f'OnBeforeClose, {browser}')
                if self._on_before_close is not None:
                    self._on_before_close()

        def show_window(self, window):
            self.list_windows.append(window)

            # Set window size
            window_info = cef.WindowInfo()
            # This call has effect only on Mac and Linux,
            #   for windows, we will use win32api to set move and set the window size. See below.
            # All rect coordinates are applied including X and Y parameters.
            window_info.SetAsChild(0, window.window_init_rect)
            window_info.windowName = window.window_title

            # CreateBrowserSync can only be called on the UI thread
            window.browser = cef.CreateBrowserSync(
                url=window.page_uri(),
                window_title=window.window_title,
                window_info=window_info,
                settings={'file_access_from_file_urls_allowed': True, }
            )

            window.browser.SetClientHandler(self._CEFLoadHandler(
                on_dom_ready=window._on_dom_ready,
                on_before_close=window._on_before_close,
            ))

            if platform.system() == "Windows":
                # Set the window size on Windows
                window_handle = window.browser.GetOuterWindowHandle()
                insert_after_handle = 0
                # X and Y parameters are ignored by setting the SWP_NOMOVE flag
                SWP_NOMOVE = 0x0002
                # noinspection PyUnresolvedReferences
                ctypes.windll.user32.SetWindowPos(window_handle, insert_after_handle,
                                                  *window.window_init_rect, SWP_NOMOVE)

    def __init__(self):
        # super().__init__(name='WindowManagingThread--UIThread')
        self.window_manager = self.WindowManager()
        self.ui_exec_queue = Queue()
        self._evt_stop = Event()
        self._cef_init()

    @staticmethod
    def _cef_init():
        # To shutdown all CEF processes on error
        sys.excepthook = cef.ExceptHook

        cef.Initialize(
            settings={
                # "product_version": "MyProduct/10.00",
                # "user_agent": "MyAgent/20.00 MyProduct/10.00",
                # 'context_menu': {'enabled': False},
                'downloads_enabled': False
            }, switches={
                'allow_file_access': b'1',
                'allow_file_access_from_files': b'1'
            })

    def run(self):
        """
        Start the UI message loop. This is be called on the main thread
        :return:
        """
        assert threading.current_thread() is threading.main_thread()

        self._evt_stop.clear()
        # This is the UI Thread
        while not self._evt_stop.is_set():
            # Todo Call this in some sort of period to increase performance
            cef.MessageLoopWork()
            try:
                func = self.ui_exec_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                if func:
                    func()

        logger.debug('messaging loop exited')
        cef.Shutdown()

    def run_on_ui_thread(self, func, *args, **kwargs):
        """
        Run some thing on th UI thread

        :param func:
        :return:
        """
        # cef.PostTask(cef.TID_UI, func, *args, **kwargs)
        self.ui_exec_queue.put(partial(func, *args, **kwargs))

    def window_show(self, window):
        self.run_on_ui_thread(self.window_manager.show_window, window)

    def shutdown(self):
        self._evt_stop.set()


class RuntimeManager:

    __instance = None

    @classmethod
    def get_instance(cls) -> 'RuntimeManager':
        if RuntimeManager.__instance is None:
            RuntimeManager()
        return RuntimeManager.__instance

    def __init__(self):
        if RuntimeManager.__instance is not None:
            raise RuntimeError('This is a singleton')
        RuntimeManager.__instance = self

        # ----------------

        self.FunctionBinding = _BindFunctionThread()
        self.JavascriptReturned = _JavascriptReturnThread()
        self.WindowManager = _WindowManaging()

    def start(self):
        self.FunctionBinding.start()
        self.JavascriptReturned.start()
        self.WindowManager.run()

    def shutdown(self):
        self.FunctionBinding.stop()
        self.JavascriptReturned.stop()
        self.WindowManager.shutdown()
