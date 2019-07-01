"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date: 7/1/2019
    
"""
import puithon
from puithon.runtime import RuntimeManager


class TutorialWindow(puithon.Window):
    def on_before_close(self):
        RuntimeManager.get_instance().shutdown()


if __name__ == '__main__':
    # Initialize the window object
    window = TutorialWindow()
    # Show the window
    puithon.RuntimeManager.get_instance().WindowManager.window_show(window)
    # Start the PuiTHON event loop
    puithon.RuntimeManager.get_instance().start()
