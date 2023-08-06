"""bootstrap implementation of baseviews

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.web.views import baseviews

baseviews.ListView.listtag = 'ul'

@monkeypatch(baseviews.ListView)
def call(self, klass='list-striped', title=None, subvid=None, listid=None, **kwargs):
    """display a list of entities by calling their <item_vid> view

    :param listid: the DOM id to use for the root element
    """
    if subvid is None and 'subvid' in self._cw.form:
        subvid = self._cw.form.pop('subvid') # consume it
    if listid:
        listid = u' id="%s"' % listid
    else:
        listid = u''
    if title:
        self.w(u'<div%s class="%s"><h4>%s</h4>\n' % (listid, klass or u'', title))
        self.w(u'<%s class="%s">\n' % (self.listtag, klass or u''))
    else:
        self.w(u'<%s%s class="%s">\n' % (self.listtag, listid, klass or u''))
    for i in xrange(self.cw_rset.rowcount):
        self.cell_call(row=i, col=0, vid=subvid, klass=klass, **kwargs)
    self.w(u'</%s>\n' % self.listtag)
    if title:
        self.w(u'</div>\n')

@monkeypatch(baseviews.ListView)
def cell_call(self, row, col=0, vid=None, klass=None, **kwargs):
    self.w(u'<li class="%s">' %  (u'odd' if row%2 else u'even'))
    self.wview(self.item_vid, self.cw_rset, row=row, col=col, vid=vid, **kwargs)
    self.w(u'</li>\n')



@monkeypatch(baseviews.SameETypeListView)
def call(self,  klass='list-striped', **kwargs):
    w = self.w
    showtitle = kwargs.pop('showtitle', not 'vtitle' in self._cw.form)
    if showtitle:
        w(u'<h1>%s</h1>' % self.title)
    klass = u'' if klass is None else u' class="%s"' % klass
    w(u'<ul%s>\n' % klass)
    for i in xrange(len(self.cw_rset)):
        w(u'<li class="%s">' %  (u'odd' if i%2 else u'even'))
        self._cw.view(self.item_vid, self.cw_rset, row=i, col=0, w=w)
        w(u'</li>')
    w(u'</ul>\n')

@monkeypatch(baseviews.MetaDataView)
def cell_call(self, row, col):
    _ = self._cw._
    entity = self.cw_rset.get_entity(row, col)
    self.w(u'<p class="text-right"><small>')
    if self.show_eid:
        self.w(u'%s #%s - ' % (entity.dc_type(), entity.eid))
    if entity.modification_date != entity.creation_date:
        self.w(u'<span>%s</span> ' % _('latest update on'))
        self.w(u'<span class="value">%s</span>, '
               % self._cw.format_date(entity.modification_date))
    # entities from external source may not have a creation date (eg ldap)
    if entity.creation_date:
        self.w(u'<span>%s</span> ' % _('created on'))
        self.w(u'<span class="value">%s</span>'
               % self._cw.format_date(entity.creation_date))
    if entity.creator:
        if entity.creation_date:
            self.w(u' <span>%s</span> ' % _('by'))
        else:
            self.w(u' <span>%s</span> ' % _('created_by'))
        self.w(u'<span class="value">%s</span>' % entity.creator.name())
    meta = entity.cw_metainformation()
    if meta['source']['uri'] != 'system':
        self.w(u' (<span>%s</span>' % _('cw_source'))
        self.w(u' <span class="value">%s</span>)' % meta['source']['uri'])
    self.w(u'</small></p>')


