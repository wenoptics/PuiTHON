"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date: 7/1/2019
    
"""
from puithon import RuntimeManager, Window


class TutorialWindow(Window):
    def on_before_close(self):
        RuntimeManager.get_instance().shutdown()

    def on_window_ready(self):
        """
        Get called when the window is ready.
        :return:
        """

        @self._event_bridge('#button-ok', 'click')
        def on_button(sender, evt):
            """
            Handle button clicked event
            """
            # Find the textbox
            textbox = self._get_dom_by_selector('#textbox-name')
            # Find the result textarea
            result = self._get_dom_by_selector('#result')

            name = textbox.get_value()
            result.set_innertext(f"Hi {name}, it's great to meet you.")
            # result.set_innerhtml(f"Hi <strong>{name}</strong>, it's great to meet you.")


if __name__ == '__main__':
    # Initialize the window object
    window = TutorialWindow(winwidth=470, winheight=330)
    # Show the window
    RuntimeManager.get_instance().WindowManager.window_show(window)
    # Start the PuiTHON event loop
    RuntimeManager.get_instance().start()
