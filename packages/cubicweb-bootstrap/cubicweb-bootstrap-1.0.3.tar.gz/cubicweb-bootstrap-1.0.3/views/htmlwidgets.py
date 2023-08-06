"""bootstrap implementation of htmlwidgets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.web import htmlwidgets
from cubicweb.web.component import Separator


@monkeypatch(Separator)
def render(self, w):
    w(u'<li class="divider"></li>')


def bwcompatible_render_item(w, item):
    if hasattr(item, 'render'):
        if getattr(item, 'newstyle', False):
            if isinstance(item, Separator):
                item.render(w)
            else:
                w(u'<li>')
                item.render(w)
                w(u'</li>')
        else:
            item.render(w) # XXX displays <li> by itself
    else:
        w(u'<li>%s</li>' % item)

@monkeypatch(htmlwidgets.BoxMenu)
def _render(self):
    tag = u'li' if self.isitem else u'div'
    self.w(u'<%s class="dropdown">' % tag)
    self.w(u'<a class="dropdown-toggle" data-toggle="dropdown" href="#">'
           u'%s&nbsp;'
           u'<span class="caret"></span>'
           u'</a>' % self.label)
    self.w(u'<ul class="dropdown-menu">')
    for item in self.items:
        bwcompatible_render_item(self.w, item)
    self.w(u'</ul>')
    self.w(u'</%s>' % tag)
