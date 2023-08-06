from logilab.common.testlib import unittest_main, mock_object

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools.htmlparser import XMLValidator

class BoostrapLogFormTemplateTC(CubicWebTC):

    def _login_labels(self):
        valid = self.content_type_validators.get('text/html', XMLValidator)()
        with self.new_access(u'anon').web_request() as req:
            page = valid.parse_string(self.vreg['views'].main_template(req, 'login'))
        return page.find_tag('label')

    def test_label(self):
        self.set_option('allow-email-login', 'yes')
        self.assertEqual(self._login_labels(), ['login or email', 'password'])
        self.set_option('allow-email-login', 'no')
        self.assertEqual(self._login_labels(), ['login', 'password'])

if __name__ == '__main__':
    unittest_main()
