# -*- coding: utf-8 -*-
"""bootstrap implementation of base components

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from cubicweb.web import component

from cubes.bootstrap import monkeypatch_default_value

monkeypatch_default_value(component.CtxComponent.render_items, 'klass', u'list-unstyled')
