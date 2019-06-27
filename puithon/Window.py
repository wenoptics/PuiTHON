"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date: 6/26/2019

"""
import base64
import platform
import sys
import functools
import ctypes
from pathlib import Path
from threading import Thread

from cefpython3 import cefpython as cef

from puithon.HotDOM import HotDOM
from puithon.runtime import jsreturned

import logging
logger = logging.getLogger(__name__)


class HandlerThread:
    def __init__(self, handler):
        self.func_handler = handler

    def _handler_with_args(self, *args, **kwargs):
        Thread(name=f'{self.__class__.__name__}-{self.func_handler.__name__}',
               target=self.func_handler, args=args, kwargs=kwargs).start()

    def _handler_no_args(self):
        Thread(name=f'{self.__class__.__name__}-{self.func_handler.__name__}',
               target=self.func_handler).start()

    @property
    def handler_with_args(self):
        return self._handler_with_args

    @property
    def handler_no_args(self):
        return self._handler_no_args


class _LoadHandler:
    def __init__(self, on_dom_ready):
        self._on_dom_ready = on_dom_ready

    def OnLoadingStateChange(self, browser, is_loading, **_):
        """Called when the loading state has changed."""
        if not is_loading:
            # Loading is complete. DOM is ready.
            if self._on_dom_ready is not None:
                self._on_dom_ready()


class Window:

    JS_ENGINE_FILE = str(Path(__file__).parent / 'puithon-js' / 'engine.js')

    def __init__(self, winx=0, winy=0, winwidth=900, winheight=600, window_title=None):
        self.window_title = window_title
        self.window_init_rect = [winx, winy, winwidth, winheight]
        self.browser = None

    def _get_dom_by_selector(self, selector) -> HotDOM:
        return HotDOM(selector, self.browser)

    def _event_bridge(self, dom, event_name, new_thread=True):
        """
        A wrapper function

        Typically used as a decorator for register a event callback

        e.g.

        >>> @event_bridge('#some-id', 'click')
        >>> def some_func(sender, evt):
        >>>     pass

        :param dom:
        :param event_name:
        :param new_thread:
        :return:
        """

        def wrapper_o(func):

            ori_func = func

            # Wrap the function for value
            @functools.wraps(func)
            def dom_wrapped(sender, evt):
                ori_func(HotDOM(sender, self.browser), evt)
            func = dom_wrapped

            if new_thread:
                # Wrap with thread
                @functools.wraps(ori_func)
                def thread_wrapped(*args, **kwargs):
                    HandlerThread(dom_wrapped).handler_with_args(*args, **kwargs)
                func = thread_wrapped

            _dom = dom
            if type(dom) is str:
                _dom = self._get_dom_by_selector(dom)
            _dom.bind_event(event_name, func)

            return func

        return wrapper_o

    def page_uri(self):
        html_file = Path(__file__).with_suffix('.html')
        return f'file://{str(html_file)}'

    def close(self):
        """
        Close the window
        :return:
        """
        pass

    def _on_dom_ready(self):
        """
        Do not override this. Use .on_window_ready() instead.

        :return:
        """
        logger.debug('_on_dom_ready')

        # Subscribe current browser for javascript value returned
        jsreturned.subscribe(self.browser)

        # Get callback on engine ready
        jsreturned.on_value('_event__engine_ready',
                            lambda *_: self._on_engine_ready())

        # Inject puithonJS the engine
        self.browser.ExecuteJavascript(open(self.JS_ENGINE_FILE, 'r').read())

    def _on_engine_ready(self):
        logger.debug('_on_engine_ready')
        # Call custom callback
        self.on_window_ready()

    def on_window_ready(self):
        """
        Override this to be called on DOM ready

        :return:
        """
        pass


class WindowManager:
    def __init__(self):
        self.list_windows = []
        self._cef_init()

    def _cef_init(self):
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

    def new_window(self, window: Window):
        assert window not in self.list_windows
        self.list_windows.append(window)

    def show_window(self, window: Window):
        assert window in self.list_windows, 'use new_window() to initialize a new window'

        # Set window size
        window_info = cef.WindowInfo()
        # This call has effect only on Mac and Linux,
        #   for windows, we will use win32api to set move and set the window size. See below.
        # All rect coordinates are applied including X and Y parameters.
        window_info.SetAsChild(0, window.window_init_rect)

        window.browser = cef.CreateBrowserSync(
            url=window.page_uri(),
            window_title=window.window_title,
            window_info=window_info,
            settings={'file_access_from_file_urls_allowed': True, }
        )

        window.browser.SetClientHandler(_LoadHandler(window._on_dom_ready))

        if platform.system() == "Windows":
            # Set the window size on Windows
            window_handle = window.browser.GetOuterWindowHandle()
            insert_after_handle = 0
            # X and Y parameters are ignored by setting the SWP_NOMOVE flag
            SWP_NOMOVE = 0x0002
            # noinspection PyUnresolvedReferences
            ctypes.windll.user32.SetWindowPos(window_handle, insert_after_handle,
                                              *window.window_init_rect, SWP_NOMOVE)

    def serve(self):
        """
        Show the CEFPython window
        This method will block

        :return:
        """
        cef.MessageLoop()

        # Clean up
        cef.QuitMessageLoop()
        cef.Shutdown()

    @staticmethod
    def html_to_data_uri(html):
        """
        Utility function

        :param html:
        :return:
        """
        html = html.encode("utf-8", "replace")
        b64 = base64.b64encode(html).decode("utf-8", "replace")
        return "data:text/html;base64,{data}".format(data=b64)
