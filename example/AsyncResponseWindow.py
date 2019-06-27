import functools
import logging
from pathlib import Path

from puithon.Window import Window
from puithon.runtime import RuntimeManager


class AsyncResponseWindow(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(window_title=self.__class__.__name__, *args, **kwargs)

        self.widget_spinner = None
        # The span to show the result
        self.widget_result_text = None
        self.widget_input = None

    def page_uri(self):
        html_file = Path(__file__).with_suffix('.html')
        return f'file://{str(html_file)}'

    def spinning(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.widget_spinner.set_display()  # Show the spinner
            func(*args, **kwargs)
            self.widget_spinner.set_display_none()  # Hide the spinner

        return wrapper

    def register_handlers(self):
        # Set shortcut
        event_bridge = self._event_bridge

        # The spinner animation
        self.widget_spinner = self._get_dom_by_selector('#demo-spinner')
        self.widget_spinner.set_display_none()
        # The span to show the result
        self.widget_result_text = self._get_dom_by_selector('span#result')
        self.widget_input = self._get_dom_by_selector('#inputBox')

        @event_bridge('#ok-button', 'click')
        @self.spinning
        def get_result_slow(sender, evt):
            print('get_result_slow() get called')
            import time
            time.sleep(1)

            val = self.widget_input.get_value()
            print('inputbox =', val)

            result = f'ok! {time.time()}. input={val}'
            self.widget_result_text.set_innertext(result)
            self._get_dom_by_selector('p').set_class('success')

        @event_bridge('#ok-button-now', 'click')
        def get_result(*args, **kwargs):
            print('get_result() get called')
            val = self.widget_input.get_value()
            result = f'get_result() get called. input={val}'
            self.widget_result_text.set_innertext(result)
            self._get_dom_by_selector('p').remove_class('success')

    def on_window_ready(self):
        self.register_handlers()

    def on_before_close(self):
        # Shutdown the whole thing
        RuntimeManager.get_instance().shutdown()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    asyncWindow = AsyncResponseWindow()
    window_manager = RuntimeManager.get_instance().WindowManager
    window_manager.window_show(asyncWindow)
    RuntimeManager.get_instance().start()
