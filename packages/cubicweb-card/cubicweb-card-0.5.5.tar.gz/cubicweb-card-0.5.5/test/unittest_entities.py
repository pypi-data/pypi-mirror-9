# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""test on entities"""

from logilab.common.testlib import unittest_main
from cubicweb.devtools.testlib import CubicWebTC

class DCTitleTC(CubicWebTC):
    def test_nowikiid(self):
        req = self.request()
        venus = req.create_entity('Card', title=u"Venus",
                                  content=u"a planet")
        self.assertEqual(venus.dc_title(), 'Venus')

    def test_wikiid(self):
        req = self.request()
        venus = req.create_entity('Card', title=u"Venus",
                                  content=u"a planet", wikiid=u'Planet_Venus')
        self.assertEqual(venus.dc_title(), 'Planet_Venus')


class BreadCrumbsTC(CubicWebTC):
    def test_onecard_nowikiid(self):
        req = self.request()
        venus = req.create_entity('Card', title=u"Venus",
                                  content=u"a planet")
        breadcrumbs = venus.cw_adapt_to('IBreadCrumbs').breadcrumbs()
        self.assertListEqual([venus], breadcrumbs)

    def test_onecard(self):
        req = self.request()
        venus = req.create_entity('Card', title=u"Venus",
                                  content=u"a planet", wikiid=u"Venus")
        breadcrumbs = venus.cw_adapt_to('IBreadCrumbs').breadcrumbs()
        self.assertListEqual([venus], breadcrumbs)

    def test_twocards(self):
        """Planet and Planet/Venus"""
        req = self.request()
        planet = req.create_entity('Card', title=u"Planet",
                                   wikiid=u"Planet")
        venus = req.create_entity('Card', title=u"Venus",
                                   wikiid=u"Planet/Venus")
        breadcrumbs = venus.cw_adapt_to('IBreadCrumbs').breadcrumbs()
        self.assertListEqual([planet, venus], breadcrumbs)

    def test_onecardnested(self):
        """Planet/Venus without Planet"""
        req = self.request()
        venus = req.create_entity('Card', title=u"Venus",
                                   wikiid=u"Planet/Venus")
        breadcrumbs = venus.cw_adapt_to('IBreadCrumbs').breadcrumbs()
        self.assertListEqual(['Planet', venus], breadcrumbs[1:])

    def test_treecards_oneinexistent(self):
        """Astronomy and Astronomy/Planet/Venus (no Astronomy/Planet)"""
        req = self.request()
        astro = req.create_entity('Card', title=u"Astronomy",
                                  wikiid=u"Astronomy")
        venus = req.create_entity('Card', title=u"Venus",
                                   wikiid=u"Astronomy/Planet/Venus")
        breadcrumbs = venus.cw_adapt_to('IBreadCrumbs').breadcrumbs()
        self.assertListEqual([astro, 'Planet', venus], breadcrumbs)

    def test_treecards_oneinexistent2(self):
        """Astronomy/Planet and Astronomy/Planet/Venus (no Astronomy)"""
        req = self.request()
        planet = req.create_entity('Card', title=u"Planets",
                                   wikiid=u"Astronomy/Planet")
        venus = req.create_entity('Card', title=u"Venus",
                                   wikiid=u"Astronomy/Planet/Venus")
        breadcrumbs = venus.cw_adapt_to('IBreadCrumbs').breadcrumbs()
        self.assertListEqual(['Astronomy', planet, venus], breadcrumbs[1:])


if __name__ == '__main__':
    unittest_main()
