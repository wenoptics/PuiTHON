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
        print(f'event "{event_name}" bind with {handler}')
        raise NotImplementedError()

    def set_display_none(self):
        """
        This is usually used to hide an element
        :return:
        """
        raise NotImplementedError()

    def set_display(self, mode='block'):
        raise NotImplementedError()


class HotDOM(DOM):

    def __init__(self, selector, browser):
        super().__init__(selector)
        self.browser = browser
        self.selector = selector
        self._dom_attr = {}

    @property
    def jquery_sel(self):
        return f"$('{self.selector}')"

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

    def set_innerhtml(self, s):
        pass

    def set_innertext(self, s):
        pass

    def get_innerhtml(self, s):
        pass

    def get_innertext(self, s):
        return self.execute_js(".text();", True)

    def execute_js(self, code, prepend_jquery=False):
        """
        Run raw javascript

        :param prepend_jquery:
        :param code:
        :return:
        """
        if prepend_jquery:
            code = f"{self.jquery_sel}.{code}"

        return self.browser.ExecuteJavascript(code)

    def execute_js_with_return(self, code):
        """
        Get intermediate return from
        :param code:
        :return:
        """
        self.execute_js();

    def bind_event(self, event_name, handler):
        print(f'event "{event_name}" bind with {handler}')

    def set_display_none(self):
        """
        This is usually used to hide an element
        :return:
        """
        self.execute_js(".css('display', 'none');", True)

    def set_display(self, mode='block'):
        self.execute_js(f".css('display', '{mode}');", True)
