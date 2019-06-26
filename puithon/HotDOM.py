import logging

from puithon.DOM import DOM
from puithon.runtime import get_python_callback_js_name, bind_setting

logger = logging.getLogger(__name__)


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
        self.call_engine_function('setProp', self.selector, name, value)

    def get_attr(self, name):
        return ''

    def set_class(self, class_or_list):
        self.call_engine_function('setClass', self.selector, class_or_list)

    def add_class(self, class_or_list):
        self.call_engine_function('addClass', self.selector, class_or_list)

    def remove_class(self, class_or_list):
        self.call_engine_function('removeClass', self.selector, class_or_list)

    def set_innerhtml(self, s):
        self.call_engine_function('setHtml', self.selector, s)

    def set_innertext(self, s):
        self.call_engine_function('setText', self.selector, s)

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
            if not code.startswith('.'):
                code = f"{self.jquery_sel}.{code}"
            else:
                code = f"{self.jquery_sel}{code}"

        logger.debug('execute_js', code)
        self.browser.ExecuteJavascript(code)

    def execute_js_with_return(self, code):
        """
        Get intermediate return from
        :param code:
        :return:
        """
        raise NotImplementedError()  # todo
        self.execute_js();

    def call_engine_function(self, func_name: str, *args, **kwargs):
        _ENGINE_VAR = 'puithonJS'
        if not func_name.startswith(_ENGINE_VAR + '.'):
            func_name = f'{_ENGINE_VAR}.{func_name}'
        self.browser.ExecuteFunction(func_name, *args, **kwargs)

    def bind_event(self, event_name, handler):
        js_name = get_python_callback_js_name(handler)
        logger.debug(f'"{self.selector}" "{event_name}" event bind with '
                     f'"{js_name}": {handler}')

        bind_setting.add_js_binding(self.browser, js_name, handler)
        self.call_engine_function('addBindEvent', self.selector, event_name, js_name)

    def set_display_none(self):
        """
        This is usually used to hide an element
        :return:
        """
        self.call_engine_function('setDisplay', self.selector, 'none')

    def set_display(self, mode='block'):
        self.call_engine_function('setDisplay', self.selector, mode)
