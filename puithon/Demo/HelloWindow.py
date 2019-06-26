from puithon.DOM import DOM
from puithon.Window import Window, WindowManager


class HelloWindow(Window):

    def page_uri(self):
        return WindowManager.html_to_data_uri("""
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
        """)

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


if __name__ == '__main__':

    mgr = WindowManager()

    helloWindow = HelloWindow()
    mgr.new_window(helloWindow)
    mgr.show_window(helloWindow)

    helloWindow.register_handlers()

    mgr.serve()
