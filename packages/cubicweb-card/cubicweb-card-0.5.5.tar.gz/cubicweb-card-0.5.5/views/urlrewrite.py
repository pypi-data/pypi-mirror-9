""" Specific urlrewrite for cards

:organization: Logilab
:copyright: 2001-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.web.views.urlrewrite import SchemaBasedRewriter, rgx, rgx_action

class CardURLRewriter(SchemaBasedRewriter):
    """handle path with the form::

        card/<wikiid>   -> view wiki page, wikiid can contain /

    Fall back to the `card` controller in any cases. The latter will handle
    both existent and non-existent cards.
    """
    priority = 10
    rules = [(rgx('/card/(?P<wikiid>.+)'),
              rgx_action(controller='card', formgroups=('wikiid', ))),
            ]
