
from cubicweb.predicates import match_form_params
from cubicweb.web.views import basecontrollers


class CardViewController(basecontrollers.ViewController):
    __regid__ = 'card'
    __select__ = (basecontrollers.ViewController.__select__ &
                  match_form_params('wikiid'))

    def publish(self, rset=None):
        rset = self._cw.execute('Card C WHERE C wikiid %(wikiid)s',
                                self._cw.form)
        if rset:
            # Drop wikiid from form to get the standard behaviour.
            # Otherwise, the presence of wikiid in form ensures that
            # CardDoesNotExistView is selected.
            self._cw.form.pop('wikiid')
        return super(CardViewController, self).publish(rset)
