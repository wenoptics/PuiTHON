from puithon.DOM import DOM
from puithon.HotDOM import HotDOM
from puithon.Window import Window, WindowManager


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
            
            <label for="name">Name:</label>
            <input type="text" id="name" value='twin'>
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
            sender.get_innertext('Sure!')

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
            
            <script
              src="https://code.jquery.com/jquery-3.4.1.slim.min.js"
              integrity="sha256-pasqAKBDmFT4eHoN2ndd6lN370kFiGUFyTiUHWhU7k8="
              crossorigin="anonymous">
            </script>
            
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
        self.widget_spinner = self._get_dom_by_selector('div#spinner')
        # The span to show the result
        self.widget_result_text = self._get_dom_by_selector('span#result')

        @self.spinning
        @event_bridge('#ok-button', 'click')
        def get_result_slow(sender, evt):
            import time
            time.sleep(2)

            result = {'a': 1, 'b': 2}
            self.widget_result_text.set_innertext(str(result))


if __name__ == '__main__':
    # helloWindow = HelloWindow()
    # helloWindow.register_handlers()
    # helloWindow.start()

    mgr = WindowManager()

    asyncWindow = AsyncResponseWindow()

    mgr.new_window(asyncWindow)
    mgr.show_window(asyncWindow)

    asyncWindow.register_handlers()

    mgr.serve()
