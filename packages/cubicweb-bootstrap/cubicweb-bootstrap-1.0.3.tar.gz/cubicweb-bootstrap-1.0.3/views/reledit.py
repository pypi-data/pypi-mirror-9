"""bootstrap implementation of reledit

:organization: Logilab
:copyright: 2013-2014 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from cubicweb.web.views.reledit import AutoClickAndEditFormView
AutoClickAndEditFormView._addzone = u' <span class="glyphicon glyphicon-plus"></span>'
AutoClickAndEditFormView._deletezone =  u' <span class="glyphicon glyphicon-remove"></span>'
AutoClickAndEditFormView._editzone = u' <span class="glyphicon glyphicon-pencil"></span>'

try:
    from cubes.inlinedit.views import reledit
except ImportError:
    pass
else:
    reledit.ReleditRelationFormHandler._addzone = u' <span class="glyphicon glyphicon-plus"></span>'
    reledit.ReleditFormHandler._editzone = u' <span class="glyphicon glyphicon-pencil"></span>'
    reledit.ReleditEntityFormHandler._deletezone = u' <span class="glyphicon glyphicon-remove"></span>'
