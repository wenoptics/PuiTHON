import base64
import sys
import functools

from cefpython3 import cefpython as cef

from puithon.HotDOM import HotDOM


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

    def __init__(self, height=600, width=400, window_title=None):
        self.window_title = window_title
        self.height = height
        self.width = width
        self._browser = None

    def _get_dom_by_selector(self, selector) -> HotDOM:
        return HotDOM(selector, self._browser)

    def _event_bridge(self, dom, event_name, new_thread=True):
        """
        A wrapper function

        Typically used as a decorator for a the event callbacks

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
            # @functools.wraps(func)
            # def wrapper(sender, event):
            #     pass

            _dom = dom
            if type(dom) is str:
                _dom = self._get_dom_by_selector(dom)
            _dom.bind_event(event_name, func)

            return func

        return wrapper_o

    def page_uri(self):
        raise NotImplementedError()

    def close(self):
        """
        Close the window
        :return:
        """
        pass

    def on_dom_ready(self):
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

        window._browser = cef.CreateBrowserSync(
            url=window.page_uri(),
            window_title=window.window_title,
            settings={'file_access_from_file_urls_allowed': True, }
        )

        window._browser.SetClientHandler(_LoadHandler(window.on_dom_ready))

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

