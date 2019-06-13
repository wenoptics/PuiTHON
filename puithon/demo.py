import functools


class DOM:
    """
    Mapping to the HTML DOM, provide handy method to manipulate dom element.

    todo: Can bs4 help anything here?
    """

    def __init__(self, selector):
        self.selector = selector
        self._dom_attr = {}

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

    def set_innerHTML(self, s):
        pass

    def set_innerText(self, s):
        pass

    def get_innerHTML(self, s):
        pass

    def get_innerText(self, s):
        pass

    def execute_js(self, code):
        """
        Run raw javascript

        :param code:
        :return:
        """
        pass

    def bind_event(self, event_name, handler):
        pass


class Window:

    def __init__(self, height=600, width=400):
        self.height = height
        self.width = width

    def _event_bridge(self, dom, event_name):
        def _wrapper_o(func):
            @functools.wraps(func)
            def _wrapper(sender, event):
                pass

            return _wrapper

        return _wrapper_o


class HelloWindow(Window):

    def register_handlers(self):
        # Set shortcut
        event_bridge = self._event_bridge
        textinput = DOM('#name')

        @event_bridge('#ok_button', 'click')
        def on_ok_clicked(sender: DOM, event):
            name = textinput.get_attr('value')
            print('the name is', name)
            sender.set_innerText('Sure!')


if __name__ == '__main__':
    helloWindow = HelloWindow()
