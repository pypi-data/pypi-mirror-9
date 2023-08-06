"Card unit test"
import re
from email.Header import decode_header

from logilab.mtconverter import xml_escape
from logilab.common.testlib import unittest_main

from cubicweb.devtools.testlib import CubicWebTC, MAILBOX
from cubicweb.ext.rest import rest_publish

class CardTests(CubicWebTC):

    def test_notifications(self):
        cw_card = self.request().create_entity('Card', title=u'sample card', synopsis=u'this is a sample card')
        self.assertEqual(len(MAILBOX), 0)
        self.commit()
        self.assertEqual(len(MAILBOX), 1)
        self.assertEqual(re.sub('#\d+', '#EID', MAILBOX[0].subject),
                          'New Card #EID (admin)')



class RestTC(CubicWebTC):
    def context(self):
        return self.execute('CWUser X WHERE X login "admin"').get_entity(0, 0)

    def test_card_role_create(self):
        self.assertEqual(rest_publish(self.context(), ':card:`index`'),
                          '<p><a class="doesnotexist reference" href="http://testing.fr/cubicweb/card/index">index</a></p>\n')

    def test_card_role_create_subpage(self):
        self.assertEqual(rest_publish(self.context(), ':card:`foo/bar`'),
                         '<p><a class="doesnotexist reference" href="http://testing.fr/cubicweb/card/foo/bar">foo/bar</a></p>\n')

    def test_card_role_link(self):
        self.request().create_entity('Card', wikiid=u'index', title=u'Site index page', synopsis=u'yo')
        self.assertEqual(rest_publish(self.context(), ':card:`index`'),
                          '<p><a class="reference" href="http://testing.fr/cubicweb/card/index">index</a></p>\n')

if __name__ == '__main__':
    unittest_main()
