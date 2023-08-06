"""cube-specific forms/views/actions/components

Specific views for cards

:organization: Logilab
:copyright: 2001-2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape
from logilab.common.decorators import cachedproperty

from cubicweb.predicates import is_instance, match_form_params
from cubicweb.web.views import uicfg, primary, baseviews
from cubicweb.web.views.autoform import AutomaticEntityForm
from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter

uicfg.primaryview_section.tag_attribute(('Card', 'title'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Card', 'synopsis'), 'hidden')
uicfg.primaryview_section.tag_attribute(('Card', 'wikiid'), 'hidden')

class CardPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Card')
    show_attr_label = False

    def render_entity_title(self, entity):
        self.w(u'<h1>%s</h1>' % xml_escape(entity.title))
        if entity.synopsis:
            self.w(u'<div class="summary">%s</div>'
                   % entity.printable_value('synopsis'))


class CardInlinedView(CardPrimaryView):
    """hide card title and summary"""
    __regid__ = 'inlined'
    title = _('inlined view')
    main_related_section = False

    def render_entity_title(self, entity):
        self.w(u'<div class="summary">%s</div>'
               % entity.printable_value('synopsis'))

    def content_navigation_components(self, context):
        pass


class CardDoesNotExistView(baseviews.NoResultView):
    __select__ = (baseviews.NoResultView.__select__ &
                  match_form_params('wikiid'))

    def call(self, **kwargs):
        super(CardDoesNotExistView, self).call(**kwargs)
        etype = self._cw.vreg['etypes'].etype_class('Card')
        ctx = {'url': etype.cw_create_url(self._cw,
                                          wikiid=self._cw.form['wikiid']),
               'message': xml_escape(self._cw._('This card does not exist yet.')),
               'invite': xml_escape(self._cw._('Create it?')),
               'notice': '',
              }
        if not self._cw.vreg.schema['Card'].has_perm(self._cw, 'add'):
            ctx['notice'] = xml_escape(self._cw._(' (You may need to log in first.)'))
        self.w(u'<div class="section">%(message)s '
               u'<a href="%(url)s">%(invite)s</a>%(notice)s</div>' % ctx)


class CardBreadCrumbsAdapter(IBreadCrumbsAdapter):

    __select__ = IBreadCrumbsAdapter.__select__ & is_instance('Card')

    @cachedproperty
    def dirname(self):
        if self.entity.wikiid:
            return '/'.join(self.entity.wikiid.split('/')[:-1])

    def card_from_wikiid(self, path):
        """Return the Card given its ``wikiid`` path or None"""
        rset = self._cw.execute("Card C WHERE C wikiid %(id)s", {"id": path})
        if rset:
            return rset.get_entity(0, 0)

    def parent_entity(self):
        if not self.dirname:
            # card is at root: return whatever super returns
            parent = super(CardBreadCrumbsAdapter, self).parent_entity()
        else:
            parent = self.card_from_wikiid(self.dirname)
        return parent

    def breadcrumbs(self, view=None, recurs=None):
        """Virtual hierarchy of wiki pages following a directory-like
        structure.
        """
        if self.parent_entity() or not self.dirname:
            # parent Card exists or the current Card is at the root (i.e. its
            # wikiid has no /)
            return super(CardBreadCrumbsAdapter, self).breadcrumbs(view, recurs)
        else:
            # parent card does not exist: build the (reversed) path by
            # iterating on the directory structure
            path = [self.entity]
            dirs = self.dirname.split('/')
            while dirs:
                card = self.card_from_wikiid('/'.join(dirs))
                p = [dirs.pop()]
                if card:
                    p = card.cw_adapt_to('IBreadCrumbs').breadcrumbs(view, recurs)
                path.extend(p)
            if not card:
                # last path entry is not a card
                path.append((self._cw.build_url(str(self.entity.e_schema)),
                             self._cw._('Card_plural')))
            path.reverse()
            return path

try:
    from cubes.seo.views import SitemapRule
    class CardSitemapRule(SitemapRule):
        __regid__ = 'card'
        query = 'Any X WHERE X is Card'
        priority = 1.0
except ImportError:
    pass

def registration_callback(vreg):
    vreg.register(CardPrimaryView)
    vreg.register(CardInlinedView)
    vreg.register(CardDoesNotExistView)
    vreg.register(CardBreadCrumbsAdapter)

    loaded_cubes = vreg.config.cubes()

    if 'seo' in loaded_cubes:
        vreg.register(CardSitemapRule)

    if 'preview' in loaded_cubes:
        from cubes.preview.views.forms import PreviewFormMixin
        class PreviewAutomaticEntityForm(PreviewFormMixin, AutomaticEntityForm):
            preview_mode = 'inline'
            __select__ = AutomaticEntityForm.__select__ & is_instance('Card')
        vreg.register(PreviewAutomaticEntityForm)

