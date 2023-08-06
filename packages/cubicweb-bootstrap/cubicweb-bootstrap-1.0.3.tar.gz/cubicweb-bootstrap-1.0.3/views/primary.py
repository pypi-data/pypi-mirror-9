"""bootstrap implementation of primary view

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from warnings import warn

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.web.views import primary


@monkeypatch(primary.PrimaryView)
def render_entity(self, entity):
    self.render_entity_toolbox(entity)
    self.render_entity_title(entity)
    # entity's attributes and relations, excluding meta data
    # if the entity isn't meta itself
    if self.is_primary():
        boxes = self._prepare_side_boxes(entity)
    else:
        boxes = None
    if boxes or hasattr(self, 'render_side_related'):
        self.w(u'<div class="row">'
               u'<div class="col-md-8">')
    self.content_navigation_components('navcontenttop')
    self.render_entity_attributes(entity)
    if self.main_related_section:
        self.render_entity_relations(entity)
    self.content_navigation_components('navcontentbottom')
    # side boxes
    if boxes or hasattr(self, 'render_side_related'):
        self.w(u'</div>' # </col-md-8>
               u'<div class="col-md-4">')
        self.render_side_boxes(boxes)
        self.w(u'</div>'  # </col-md-4>
               u'</div>') # </row>


@monkeypatch(primary.PrimaryView)
def render_entity_attributes(self, entity):
    """Renders all attributes and relations in the 'attributes' section.
    """
    display_attributes = []
    for rschema, _, role, dispctrl in self._section_def(entity, 'attributes'):
        vid = dispctrl.get('vid', 'reledit')
        if rschema.final or vid == 'reledit' or dispctrl.get('rtypevid'):
            value = entity.view(vid, rtype=rschema.type, role=role,
                                initargs={'dispctrl': dispctrl})
        else:
            rset = self._relation_rset(entity, rschema, role, dispctrl)
            if rset:
                value = self._cw.view(vid, rset)
            else:
                value = None
        if value is not None and value != '':
            display_attributes.append( (rschema, role, dispctrl, value) )
    if display_attributes:
        # bs customization begins
        self.w(u'<table class="table cw-table-primary-entity">')
        # bs customization ends
        for rschema, role, dispctrl, value in display_attributes:
            label = self._rel_label(entity, rschema, role, dispctrl)
            self.render_attribute(label, value, table=True)
        self.w(u'</table>')

@monkeypatch(primary.PrimaryView)
def render_relation(self, label, value):
    self.w(u'<div class="panel panel-default relations">')
    if label:
        self.w(u'<div class="panel-heading panel-title">%s</div>' % label)
    self.w(u'<div class="panel-body">')
    self.w(value)
    self.w(u'</div>')
    self.w(u'</div>')

@monkeypatch(primary.RelatedView)
def call(self, **kwargs):
    if 'dispctrl' in self.cw_extra_kwargs:
        if 'limit' in self.cw_extra_kwargs['dispctrl']:
            limit = self.cw_extra_kwargs['dispctrl']['limit']
        else:
            limit = self._cw.property_value('navigation.related-limit')
        list_limit = self.cw_extra_kwargs['dispctrl'].get('use_list_limit', 5)
        subvid = self.cw_extra_kwargs['dispctrl'].get('subvid', 'incontext')
    else:
        limit = list_limit = None
        subvid = 'incontext'
    if limit is None or self.cw_rset.rowcount <= limit:
        if self.cw_rset.rowcount == 1:
            self.wview(subvid, self.cw_rset, row=0)
        elif list_limit is None or 1 < self.cw_rset.rowcount <= list_limit:
            self.wview('csv', self.cw_rset, subvid=subvid)
        else:
            # bs customization begins
            self.wview('list', self.cw_rset, subvid=subvid, klass='list-unstyled')
            # bs customization ends
    # else show links to display related entities
    else:
        rql = self.cw_rset.printable_rql()
        rset = self.cw_rset.limit(limit) # remove extra entity
        if list_limit is None:
            self.wview('csv', rset, subvid=subvid)
            self.w(u'<a href="%s" class="see-all">%s</a>' % (
                xml_escape(self._cw.build_url(rql=rql, vid='list', subvid=subvid)),
                self._cw._('see them all')))
        else:
            self.w(u'<div>')
            # bs customization begins
            self.wview('list', rset, subvid=subvid, klass='list-unstyled')
            # bs customization ends
            self.w(u'<a href="%s" class="see-all">%s</a>' % (
                xml_escape(self._cw.build_url(rql=rql, vid='list', subvid=subvid)),
                self._cw._('see them all')))
            self.w(u'</div>')
