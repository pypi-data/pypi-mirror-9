"""bootstrap implementation of cwproperty view

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from cubicweb.web.views.cwproperties import  SystemCWPropertiesForm, \
     make_togglable_link

@monkeypatch(SystemCWPropertiesForm)
def wrap_main_form(self, group, label, form):
    label += u' <span class="caret"></span>'
    status = self._group_status(group)
    cssclass = 'panel-body %s' % status if status else 'panel-body'
    self.w(u'<div class="panel panel-default">'
           u'<div class="panel-heading">%s</div>\n' %
           (make_togglable_link('fieldset_' + group, label)))
    self.w(u'<div class="%s" id="fieldset_%s">' % (cssclass, group))
    self.w(form)
    self.w(u'</div>')
    self.w(u'</div>')

@monkeypatch(SystemCWPropertiesForm)
def wrap_grouped_form(self, group, label, objects):
    label += u' <span class="caret"></span>'
    status = self._group_status(group)
    cssclass = 'panel-body %s' % status if status else 'panel-body'
    self.w(u'<div class="panel panel-default">'
           u'<div class="panel-heading">%s</div>\n' %
           (make_togglable_link('fieldset_' + group, label)))
    self.w(u'<div class="%s" id="fieldset_%s">' % (cssclass, group))

    sorted_objects = sorted((self._cw.__('%s_%s' % (group, o)), o, f)
                            for o, f in objects.iteritems())
    for label, oid, form in sorted_objects:
        self.wrap_object_form(group, oid, label, form)
    self.w(u'</div>')
    self.w(u'</div>')
