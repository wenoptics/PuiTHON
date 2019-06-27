import logging

from puithon.HotDOM import HotDOM
from puithon.Window import Window
from puithon.runtime import RuntimeManager


class HelloWindowParent(Window):

    def __init__(self, win_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.win_manager = win_manager
        self.wg_textinput = None

        # Define the child window
        self.win_popup = HelloWindowChild(winwidth=300, winheight=200)
        self.win_popup.parent_window = self

    def page_uri(self):
        return self.html_to_data_uri("""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
            
            <label for="name">Name:</label>
            <input type="text" id="parentTextarea" value='twin'>
            <button id="post-button">Post</button>
            
            </body>
            </html>
        """)

    def register_handlers(self):
        # Set shortcut
        event_bridge = self._event_bridge

        # The widget to get the 'name' from user input
        self.wg_textinput = self._get_dom_by_selector('#parentTextarea')

        @event_bridge('#post-button', 'click')
        def on_ok_clicked(sender: HotDOM, event):
            input_text = self.wg_textinput.get_value()
            print(f'the test is "{input_text}"')
            if not self.win_popup.is_ready:
                # Bring up the window
                self.win_manager.window_show(self.win_popup)
            else:
                # The child window is already shown
                self.win_popup.wg_textarea.set_innertext(input_text)
            sender.set_innertext('Posted!')

        @event_bridge(self.wg_textinput, 'keyup')
        def on_input_text_change(sender: HotDOM, event):
            print('keyup: value =', sender.get_value())

    def on_window_ready(self):
        self.register_handlers()

    def on_before_close(self):
        # Shutdown the whole thing
        RuntimeManager.get_instance().shutdown()


class HelloWindowChild(Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_window = None
        self.wg_textarea = None

    def page_uri(self):
        return self.html_to_data_uri("""
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
            </head>
            <body>
            
            <p id="textarea" style='height: 80vh; width: 80vw; background-color: lightgray'></p>
            
            </body>
        </html>
        """)

    def on_window_ready(self):
        self.wg_textarea = self._get_dom_by_selector('#textarea')
        if self.parent_window is not None:
            # Get the parent window text
            self.wg_textarea.set_innertext(self.parent_window.wg_textinput.get_value())

    def on_before_close(self):
        print('child window closing')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    window_manager = RuntimeManager.get_instance().WindowManager
    # Create the parent window
    win_parent = HelloWindowParent(window_manager, winheight=500, winwidth=700)
    window_manager.window_show(win_parent)
    RuntimeManager.get_instance().start()
