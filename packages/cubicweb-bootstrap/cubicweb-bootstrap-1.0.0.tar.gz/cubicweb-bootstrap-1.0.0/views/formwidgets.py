"""bootstrap implementation of formwidgets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.web import formwidgets


formwidgets.ButtonInput.css_class = 'btn btn-default'
formwidgets.Button.css_class = 'btn btn-default'
formwidgets.SubmitButton.css_class = 'btn btn-primary'
