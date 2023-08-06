# -*- coding: utf-8 -*-
"""bootstrap implementation of startup views

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.common.textutils import unormalize
from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.web.views import startup, uicfg

startup.ManageView.box_html = u'''<div class="panel panel-default">
    <div class="panel-heading panel-title">%(title)s</div>
    <div class="panel-body">%(content)s</div>
    </div>'''

@monkeypatch(startup.ManageView)
def manage_actions(self):
    allactions = self._cw.vreg['actions'].possible_actions(self._cw)
    if allactions.get('manage'):
        html = []
        w = html.append
        w(u'<ul>')
        for action in allactions['manage']:
            w(u'<li><a href="%s">%s</a></li>' % (
                action.url(), self._cw._(action.title)))
        w(u'</ul>')
        self.w(self.box_html % {'title' : self._cw._('Manage'),
                            'content': u'\n'.join(html)})


@monkeypatch(startup.ManageView)
def startup_views(self):
    views = [v for v in self._cw.vreg['views'].possible_views(self._cw, None)
             if v.category == 'startupview'
             and v.__regid__ not in self.skip_startup_views]
    if not views:
        return
    html = []
    w = html.append
    w(u'<ul>')
    for v in sorted(views, key=lambda x: self._cw._(x.title)):
        w('<li><a href="%s">%s</a></li>' % (
            xml_escape(v.url()), xml_escape(self._cw._(v.title).capitalize())))
    w(u'</ul>')
    self.w(self.box_html % {'title' : self._cw._('Startup views'),
                            'content': u'\n'.join(html)})

@monkeypatch(startup.ManageView)
def entities(self):
    schema = self._cw.vreg.schema
    eschemas = [eschema for eschema in schema.entities()
                if uicfg.indexview_etype_section.get(eschema) == 'application']
    if eschemas:
        html = self.entity_types_table(eschemas)
        self.w(self.box_html % {'title' : self._cw._('Browse by entity type'),
                                'content': u'\n'.join(html)})

@monkeypatch(startup.ManageView)
def entity_types_table(self, eschemas):
    infos = sorted(self.entity_types(eschemas),
                   key=lambda (l,a,e): unormalize(l))
    q, r = divmod(len(infos), 2)
    html = []
    w = html.append
    w(u'<div class="row">')
    for links in (infos[:q+r], infos[q+r:]):
        if links:
            w(u'<div class="col-md-6">')
            w(u'<ul class="list-unstyled">')
            for (_, etypelink, addlink) in links:
                w('<li>%s %s</li>' % (addlink,  etypelink))
            w(u'</ul>')
            w(u'</div>')
    w(u'</div>')
    return html
