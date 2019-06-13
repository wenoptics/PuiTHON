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
        pass

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


if __name__ == '__main__':

    window = Window()

    textinput = DOM('#name')

    @event_bridge('#ok_button', 'click')
    def on_ok_clicked(sender: DOM, event):
        name = textinput.get_attr('value')
        print('name is', name)
        sender.set_innerText('Sure!')

