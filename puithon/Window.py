"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date: 6/26/2019

"""

import functools
import inspect
import time
from enum import Enum
from pathlib import Path
from random import random
from threading import Thread

from puithon.HotDOM import HotDOM

import logging

from puithon.runtime import RuntimeManager

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


class Window:

    class WindowStatus(Enum):
        INIT = 0
        SHOWN = 1
        READY = 2
        DESTROYED = 3

    JS_ENGINE_FILE = str(Path(__file__).parent / 'puithon-js' / 'engine.js')

    def __init__(self, winx=0, winy=0, winwidth=900, winheight=600, window_title=None):
        """

        :param winx: Window location left in pixel (Not working on Windows)
        :param winy: Window location top in pixel (Not working on Windows)
        :param winwidth: Window size
        :param winheight: Window size
        :param window_title: Window title, default to the class name
        """
        if window_title is None:
            window_title = self.__class__.__name__
        self.window_title = window_title
        self.window_init_rect = [winx, winy, winwidth, winheight]
        self.browser = None
        self._status = self.WindowStatus.INIT

    @staticmethod
    def html_to_data_uri(html):
        """
        Utility function

        :param html:
        :return:
        """
        import base64
        html = html.encode("utf-8", "replace")
        b64 = base64.b64encode(html).decode("utf-8", "replace")
        return "data:text/html;base64,{data}".format(data=b64)

    def call_engine_function(self, func_name: str, *args, **kwargs):
        _ENGINE_VAR = 'puithonJS'
        if not func_name.startswith(_ENGINE_VAR + '.'):
            func_name = f'{_ENGINE_VAR}.{func_name}'
        self.browser.ExecuteFunction(func_name, *args, **kwargs)

    def run_javascript(self, code_str):
        """
        Run raw javascript code. This will run asynchronously and will not return anything.
        To receive results from javascript, use `.run_javascript_with_result()`.

        todo: Javascript exception
        :param code_str: Javascript code string
        :return:
        """
        self.browser.ExecuteJavascript(str(code_str))

    def run_javascript_with_result(self, code_str):
        """
        Blocking and waiting for result

        :param code_str:
        :return:
        """
        assert self._status is self.WindowStatus.READY, 'This method can only be called after the window is ready'

        _uniq_key = hex(hash(f'{time.time()}-{random()}'))
        self.call_engine_function('executeThenPoll', _uniq_key, code_str)
        return RuntimeManager.get_instance().JavascriptReturned.wait_for_value(_uniq_key)

    def show_alert(self, text: str):
        """
        Show a javascript alert.

        :param text:
        :return:
        """
        # todo|fixme escaping issue. e.g. \n in text
        text = str(text).replace('\n', '\\n').replace('\r', '\\r')
        self.browser.ExecuteJavascript(f'alert("{text}")')

    def _get_dom_by_selector(self, selector) -> HotDOM:
        # todo Potentially, the self.browser can be None.
        #   Thus the best practice to call this function is after dom is ready (i.e. in on_window_ready())
        #   Pass the `browser` somewhere/sometime-later to get better flexibility.
        if self.browser is None:
            logging.warning('self.browser is None. Consider to call this after DOM is ready. '
                            'e.g. Call this in .on_window_ready()')
        return HotDOM(selector, self.browser)

    def _event_bridge(self, dom, event_name):
        """
        A wrapper function. The wrapped handler will be run in a new thread

        Typically used as a decorator for register a event callback

        e.g.

        >>> @event_bridge('#some-id', 'click')
        >>> def some_func(sender, evt):
        >>>     pass

        :param dom:
        :param event_name:
        :return:
        """

        def wrapper_o(func):

            ori_func = func

            # Wrap the function for value
            @functools.wraps(func)
            def dom_wrapped(sender, evt):
                ori_func(HotDOM(sender, self.browser), evt)
            func = dom_wrapped

            new_thread = True
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
        _file = inspect.getfile(self.__class__)
        html_file = Path(_file).with_suffix('.html').resolve()  # instead of using just __file__
        # assert html_file.is_file()
        logger.debug(f'loading html file "{html_file}"')
        return f'file://{str(html_file)}'

    def close(self):
        """
        Close the window
        :return:
        """
        # todo

    def _on_dom_ready(self):
        """
        Do not override this. Use .on_window_ready() instead.

        :return:
        """
        logger.debug('_on_dom_ready')
        self._status = self.WindowStatus.SHOWN

        # Subscribe current browser for javascript value returned
        RuntimeManager.get_instance().JavascriptReturned.subscribe(self.browser)

        # Get callback on engine ready
        RuntimeManager.get_instance().JavascriptReturned\
            .on_value('_event__engine_ready', lambda *_: self._on_engine_ready())

        # Inject puithonJS the engine
        self.browser.ExecuteJavascript(open(self.JS_ENGINE_FILE, 'r').read())

    def _on_engine_ready(self):
        """
        Do not override this
        :return:
        """
        logger.debug('_on_engine_ready')

        self._status = self.WindowStatus.READY

        # Call custom callback
        self.on_window_ready()

    def _on_before_close(self):
        logger.debug('_on_before_close')
        self.on_before_close()
        self._status = self.WindowStatus.DESTROYED

    def on_window_ready(self):
        """
        Override this to be called on DOM ready

        :return:
        """
        pass

    def on_before_close(self):
        """
        Override this to be called before the window is closed

        :return:
        """
        pass

    @property
    def is_ready(self):
        return self._status is self.WindowStatus.READY

    @property
    def is_shown(self):
        return self._status is self.WindowStatus.SHOWN
