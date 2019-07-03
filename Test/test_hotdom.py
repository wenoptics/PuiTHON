"""
Framework PuiTHON

    @author: Grayson Wen
    @email: wenoptics@gmail.com
    @date: 7/3/2019
    
"""
import time
import unittest

from puithon import Window, RuntimeManager


class TWin(Window):
    def page_uri(self):
        return self.html_to_data_uri("""
            <html>
            <body>
                <div id='test-div'>div text</div>
                <a id='test-link' href='#href'>link</a>
                <div id='nest-div'><span>Hi span</span></div>
            </body>
            </html>
        """)


class TestHotDOM(unittest.TestCase):
    window = None

    def test_all(self):
        self.window = TWin()
        RuntimeManager.get_instance().WindowManager.window_show(self.window)

        def test():
            print('------- testing get/set html -------')
            div = self.window._get_dom_by_selector('#nest-div')
            self.assertEqual(div.get_innerhtml(), '<span>Hi span</span>')

            new_html = '<span>Hi span new</span>'
            div.set_innerhtml(new_html)
            time.sleep(1)
            self.assertEqual(div.get_innerhtml(), new_html)

            print('------- testing get/set text -------')
            div_2 = self.window._get_dom_by_selector('#test-div')
            self.assertEqual(div_2.get_innertext(), 'div text')

            new_text = 'div new text'
            div_2.set_innertext(new_text)
            time.sleep(1)
            self.assertEqual(div_2.get_innertext(), new_text)

            print('------- testing get/set attribute -------')
            link = self.window._get_dom_by_selector('#test-link')
            self.assertEqual(link.get_attr('href'), '#href')

            new_href = '#href_2'
            link.set_attr('href', new_href)
            time.sleep(1)
            self.assertEqual(link.get_attr('href'), new_href)

            print(' ------- All done, tearing down')
            RuntimeManager.get_instance().shutdown()

        self.window.on_window_ready = test
        RuntimeManager.get_instance().start()


if __name__ == '__main__':
    TestHotDOM()
