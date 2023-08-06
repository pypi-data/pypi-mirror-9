from logilab.common.testlib import unittest_main, tag

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.devtools.htmlparser import XMLValidator


class BoostrapTheMainTemplateTC(CubicWebTC):

    @tag('index')
    def test_valid_xhtml_index(self):
        with self.admin_access.web_request() as req:
            self.view('index', req=req)

    @tag('error')
    def test_valid_xhtml_error(self):
        valid = self.content_type_validators.get('text/html', XMLValidator)()
        with self.admin_access.web_request() as req:
            page = valid.parse_string(self.vreg['views'].main_template(req, 'error-template'))

if __name__ == '__main__':
    unittest_main()
