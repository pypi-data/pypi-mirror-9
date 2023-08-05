"""bootstrap implementation of tabs

:organization: Logilab
:copyright: 2014 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb import utils
from cubicweb.web.views import tabs


@monkeypatch(tabs.TabsMixin)
def render_tabs(self, tabs, default, entity=None):
    # delegate to the default tab if there is more than one entity
    # in the result set (tabs are pretty useless there)
    if entity and len(self.cw_rset) > 1:
        entity.view(default, w=self.w)
        return
    self._cw.add_js(('cubicweb.ajax.js', 'jquery.cookie.js'))
    # prune tabs : not all are to be shown
    tabs, active_tab = self.prune_tabs(tabs, default)
    # build the html structure
    w = self.w
    uid = entity and entity.eid or utils.make_uid('tab')
    w(u'<div id="entity-tabs-%s" class="entity-tabs">' % uid)
    w(u'<ul class="nav nav-tabs">')
    for i, (tabid, domid, tabkwargs) in enumerate(tabs):
        if domid == active_tab:
            w(u'<li class="active">')
        else:
            w(u'<li>')
        w(u'<a href="#%s" data-toggle="tab">' % domid)
        w(tabkwargs.pop('label', self._cw._(tabid)))
        w(u'</a>')
        w(u'</li>')
    w(u'</ul>')
    w(u'<div class="tab-content">')
    for tabid, domid, tabkwargs in tabs:
        active = u'active' if domid == active_tab else u''
        w(u'<div id="%s" class="tab-pane %s">' % (domid, active))
        if self.lazy:
            tabkwargs.setdefault('tabid', domid)
            tabkwargs.setdefault('vid', tabid)
            self.lazyview(**tabkwargs)
        else:
            self._cw.view(tabid, w=self.w, **tabkwargs)
        w(u'</div>')
    w(u'</div>')
    w(u'</div>')
    # XXX make work history: true
    if self.lazy:
        self._cw.add_onload(u"""
        $('#entity-tabs-%(uid)s a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
            var tabid = $(e.target).attr('href').slice(1);
            setTab(tabid, '%(cookiename)s');
        });
        setTab('%(domid)s', '%(cookiename)s');
        """ % {'domid'      : active_tab,
               'uid'        : uid,
               'cookiename' : self.cookie_name})
