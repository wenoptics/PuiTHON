import base64
import functools
import sys
from cefpython3 import cefpython as cef


class DOM:
    """
    Mapping to the HTML DOM, provide handy method to manipulate dom element.

    todo: Can bs4 help anything here?
    """

    def __init__(self, selector):
        self.selector = selector
        self._dom_attr = {}

    def set_attr(self, name, value):
        raise NotImplementedError()

    def get_attr(self, name):
        raise NotImplementedError()

    def set_class(self, class_or_list):
        raise NotImplementedError()

    def add_class(self, class_):
        raise NotImplementedError()

    def remove_class(self, class_):
        raise NotImplementedError()

    def set_innerhtml(self, s):
        raise NotImplementedError()

    def set_innertext(self, s):
        raise NotImplementedError()

    def get_innerhtml(self, s):
        raise NotImplementedError()

    def get_innertext(self, s):
        raise NotImplementedError()

    def execute_js(self, code):
        """
        Run raw javascript

        :param code:
        :return:
        """
        raise NotImplementedError()

    def bind_event(self, event_name, handler):
        print(f'event "{event_name}" bind with {handler}')
        raise NotImplementedError()

    def set_display_none(self):
        """
        This is usually used to hide an element
        :return:
        """
        raise NotImplementedError()

    def set_display(self, mode='block'):
        raise NotImplementedError()


class HotDOM(DOM):

    def __init__(self, selector, browser: Browser):
        super().__init__(selector)
        self.browser = browser
        self.selector = selector
        self._dom_attr = {}

    @property
    def jquery_sel(self):
        return f"$('{self.selector}')"

    def set_attr(self, name, value):
        pass

    def get_attr(self, name):
        return ''

    def set_class(self, class_or_list):
        pass

    def add_class(self, class_):
        pass

    def remove_class(self, class_):
        pass

    def set_innerhtml(self, s):
        pass

    def set_innertext(self, s):
        pass

    def get_innerhtml(self, s):
        pass

    def get_innertext(self, s):
        return self.execute_js(".text();", True)

    def execute_js(self, code, prepend_jquery=False):
        """
        Run raw javascript

        :param prepend_jquery:
        :param code:
        :return:
        """
        if prepend_jquery:
            code = f"{self.jquery_sel}.{code}"

        return self.browser.ExecuteJavascript(code)

    def execute_js_with_return(self, code):
        self.execute_js();

    def bind_event(self, event_name, handler):
        print(f'event "{event_name}" bind with {handler}')

    def set_display_none(self):
        """
        This is usually used to hide an element
        :return:
        """
        self.execute_js(".css('display', 'none');", True)

    def set_display(self, mode='block'):
        self.execute_js(f".css('display', '{mode}');", True)


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
            url=self.html_to_data_uri(self.get_html()),
            window_title=self.window_title,
            settings={'file_access_from_file_urls_allowed': True, }
        )

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


class Window:

    def __init__(self, height=600, width=400, window_title=None):
        self.window_title = window_title
        self.height = height
        self.width = width
        self._browser = None

    def _get_dom_by_selector(self, selector):
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

    def get_html(self):
        raise NotImplementedError()

    def close(self):
        """
        Close the window
        :return:
        """
        pass


class HelloWindow(Window):

    def get_html(self):
        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>HelloWindow</title>
            </head>
            <body>
            
            <label for="name">Name:</label><input type="text" id="name">
            <button id="ok-button">OK</button>
            
            </body>
            </html>
        """

    def register_handlers(self):
        # Set shortcut
        event_bridge = self._event_bridge

        # The widget to get the 'name' from user input
        textinput = DOM('#name')

        @event_bridge('#ok-button', 'click')
        def on_ok_clicked(sender: DOM, event):
            name = textinput.get_attr('value')
            print('the name is', name)
            sender.set_innerText('Sure!')

        @event_bridge(textinput, 'change')
        def on_input_text_change(sender: DOM, event):
            print('onChange: name =', sender.get_attr('value'))


class AsyncResponseWindow(Window):

    def __init__(self, height=600, width=400, window_title=None):
        window_title = self.__class__.__name__ if window_title is None else window_title
        super().__init__(height=height, width=width, window_title=window_title)

        self.widget_spinner: DOM = DOM('')
        # The span to show the result
        self.widget_result_text: DOM = DOM('')

    def get_html(self):
        return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>AsyncResponseWindow</title>
            </head>
            <body>
            
            <label for="inputBox">Input:</label><input type="text" id="inputBox">
            <button id="ok-button">Get Time Consuming Result</button>
            <p>
                Result:
                <span id='result'></span>
            </p>
            
            </body>
            </html>
        """

    def spinning(self, func):
        def wrapper(*args, **kwargs):
            self.widget_spinner.set_display()  # Show the spinner
            func(*args, **kwargs)
            self.widget_spinner.set_display_none()  # Hide the spinner

        return wrapper

    def register_handlers(self):
        # Set shortcut
        event_bridge = self._event_bridge

        # The spinner animation
        self.widget_spinner = DOM('div#spinner')
        # The span to show the result
        self.widget_result_text = DOM('span#result')

        @self.spinning
        @event_bridge('#ok-button', 'click')
        def get_result_slow(sender, evt):
            import time
            time.sleep(2)

            result = {'a': 1, 'b': 2}
            self.widget_result_text.set_innerText(str(result))


if __name__ == '__main__':
    # helloWindow = HelloWindow()
    # helloWindow.register_handlers()
    # helloWindow.start()

    mgr = WindowManager()

    asyncWindow = AsyncResponseWindow()
    asyncWindow.register_handlers()

    mgr.new_window(asyncWindow)
    mgr.show_window(asyncWindow)

    mgr.serve()
