import logging

logger = logging.getLogger(__name__)


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
        raise NotImplementedError()

    def set_display_none(self):
        """
        This is usually used to hide an element
        :return:
        """
        raise NotImplementedError()

    def set_display(self, mode='block'):
        raise NotImplementedError()


