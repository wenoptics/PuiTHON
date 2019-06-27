import logging
logging.basicConfig(level=logging.DEBUG)

from puithon.HotDOM import HotDOM
from puithon.Window import Window
from puithon.runtime import window_managing


class HelloWindow(Window):

    def page_uri(self):
        return self.html_to_data_uri("""
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
            <button id="reset-button">Reset</button>
            
            </body>
            </html>
        """)

    def register_handlers(self):
        # Set shortcut
        event_bridge = self._event_bridge

        # The widget to get the 'name' from user input
        textinput = self._get_dom_by_selector('#name')

        @event_bridge('#ok-button', 'click')
        def on_ok_clicked(sender: HotDOM, event):
            name = textinput.get_value()
            print(f'the name is "{name}"')
            sender.set_innertext('Sure!')

        @event_bridge(textinput, 'keyup')
        def on_input_text_change(sender: HotDOM, event):
            print('keyup: value =', sender.get_value())

        @event_bridge('#reset-button', 'click')
        def on_reset(sender: HotDOM, event):
            self._get_dom_by_selector('#ok-button').set_innertext('OK')

    def on_window_ready(self):
        self.register_handlers()


if __name__ == '__main__':
    helloWindow = HelloWindow(winheight=500, winwidth=500)
    window_managing.window_show(helloWindow)
    window_managing.run()



