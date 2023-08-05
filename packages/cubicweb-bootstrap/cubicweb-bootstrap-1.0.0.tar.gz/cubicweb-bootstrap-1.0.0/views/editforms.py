"""bootstrap implementation of autoforms

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from cubicweb.web.views import editforms

@monkeypatch(editforms.EditionFormView)
def form_title(self, entity):
    """the form view title"""
    ptitle = self._cw._(self.title)
    self.w(u'<div class="formTitle"><h1>%s %s</h1></div>' % (
        entity.dc_type(), ptitle and '(%s)' % ptitle))

@monkeypatch(editforms.CreationFormView)
def form_title(self, entity):
    """the form view title"""
    if '__linkto' in self._cw.form:
        if isinstance(self._cw.form['__linkto'], list):
            # XXX which one should be considered (case: add a ticket to a
            # version in jpl)
            rtype, linkto_eid, role = self._cw.form['__linkto'][0].split(':')
        else:
            rtype, linkto_eid, role = self._cw.form['__linkto'].split(':')
        linkto_rset = self._cw.eid_rset(linkto_eid)
        linkto_type = linkto_rset.description[0][0]
        if role == 'subject':
            title = self._cw.__('creating %s (%s %s %s %%(linkto)s)' % (
                entity.e_schema, entity.e_schema, rtype, linkto_type))
        else:
            title = self._cw.__('creating %s (%s %%(linkto)s %s %s)' % (
                entity.e_schema, linkto_type, rtype, entity.e_schema))
        msg = title % {'linkto' : self._cw.view('incontext', linkto_rset)}
        # bs customization begins
        self.w(u'<div class="formTitle notransform"><h1>%s</h1></div>' % msg)
        # bs customization ends
    else:
        super(editforms.CreationFormView, self).form_title(entity)
