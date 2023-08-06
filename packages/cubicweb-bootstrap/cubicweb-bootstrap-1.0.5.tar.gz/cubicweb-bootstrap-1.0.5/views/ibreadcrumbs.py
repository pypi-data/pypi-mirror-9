"""bootstrap implementation of ibreadcrumbs

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.entity import Entity
from cubicweb.web.views import ibreadcrumbs


ibreadcrumbs.BreadCrumbEntityVComponent.css_class = u'breadcrumb'


@monkeypatch(ibreadcrumbs.BreadCrumbEntityVComponent)
def open_breadcrumbs(self, w):
    w(u'<ul id="breadcrumbs" class="%s">' % self.css_class)


@monkeypatch(ibreadcrumbs.BreadCrumbEntityVComponent)
def close_breadcrumbs(self, w):
    w(u'</ul>')


@monkeypatch(ibreadcrumbs.BreadCrumbEntityVComponent)
def render_breadcrumbs(self, w, contextentity, path):
    root = path.pop(0)
    if isinstance(root, Entity):
        w(u'<li>')
        w(self.link_template % (self._cw.build_url(root.__regid__),
                                root.dc_type('plural')))
        w(u'</li>')
    liclass = u' class="active"' if not path else u''
    w(u'<li%s>' % liclass)
    self.wpath_part(w, root, contextentity, not path)
    w(u'</li>')
    for i, parent in enumerate(path):
        last = i == len(path) - 1
        liclass = u' class="active"' if last else u''
        w(u'<li%s>' % liclass)
        self.wpath_part(w, parent, contextentity, last)
        w(u'</li>')


@monkeypatch(ibreadcrumbs.BreadCrumbAnyRSetVComponent)
def render(self, w, **kwargs):
    self.open_breadcrumbs(w)
    w(u'<li class="active">')
    w(self._cw._('search'))
    w(u'</li>')
    self.close_breadcrumbs(w)
