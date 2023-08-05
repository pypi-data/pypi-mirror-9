"""bootstrap implementation of forms

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"


from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.web import formwidgets, stdmsgs
from cubicweb.web.views.forms import FieldsForm
from cubicweb.web.views.autoform import AutomaticEntityForm

from cubes.bootstrap import monkeypatch_default_value

# Forms
FieldsForm.needs_js += ('cubes.bootstrap.edition.js',)
FieldsForm.needs_css = ()
FieldsForm.cssclass = AutomaticEntityForm.cssclass = 'form-horizontal'

# Buttons
@monkeypatch(formwidgets.Button)
def render(self, form, field=None, renderer=None):
    label = form._cw._(self.label)
    attrs = self.attrs.copy()
    if self.cwaction:
        assert self.onclick is None
        attrs['onclick'] = "postForm('__action_%s', \'%s\', \'%s\')" % (
            self.cwaction, self.label, form.domid)
    elif self.onclick:
        attrs['onclick'] = self.onclick
    if self.name:
        attrs['name'] = self.name
        if self.setdomid:
            attrs['id'] = self.name
    if self.settabindex and not 'tabindex' in attrs:
        attrs['tabindex'] = form._cw.next_tabindex()
    if self.icon:
        img = u'<i class="%s"> </i>' % self.icon
    else:
        img = u''
    return tags.button(img + xml_escape(label), escapecontent=False,
                       value=label, type=self.type, **attrs)
