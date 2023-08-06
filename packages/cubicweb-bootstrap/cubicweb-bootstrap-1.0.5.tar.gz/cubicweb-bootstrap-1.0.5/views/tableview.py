# -*- coding: utf-8 -*-
"""bootstrap implementation of tableview

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.web.views import tableview

tableview.TableLayout.cssclass = 'listing table table-bordered table-condensed'


_row_attributes = tableview.TableLayout.row_attributes

@monkeypatch(tableview.TableLayout)
def row_attributes(self, rownum):
    attrs = _row_attributes(self, rownum)
    del attrs['onmouseover']
    del attrs['onmouseout']
    return attrs
