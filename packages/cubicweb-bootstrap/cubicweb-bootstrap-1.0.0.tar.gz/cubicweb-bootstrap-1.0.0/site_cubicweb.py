# -*- coding: utf-8 -*-
"""this is where you could register procedures for instance

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"

from logilab.common.configuration import REQUIRED
from logilab.common.decorators import monkeypatch

from cubicweb.web import formwidgets, stdmsgs

from cubes.bootstrap import monkeypatch_default_value

# put there monkeypatches of things that aren't reloaded automatically

# monkeypatches #############################################################

# keep the original `formwidgets.FieldWidget.attributes`
orig_attributes = formwidgets.FieldWidget.attributes

formwidgets.FieldWidget.css_class = 'form-control'

@monkeypatch(formwidgets.FieldWidget)
def attributes(self, form, field):
    """ add the bootstrap `form-control` class to formwidgets.FieldWidget.attributes method
    """
    attrs = orig_attributes(self, form, field)
    if self.css_class:
        attrs['class'] = ' '.join((attrs.get('class', ''),
                                   self.css_class)).strip()
    return attrs

# in bootstrap 3.0.0 CheckBox, RadioBox and FileInput must not have
# form-control class
formwidgets.CheckBox.attributes = orig_attributes
formwidgets.FileInput.attributes = orig_attributes


# Buttons
stdmsgs.BUTTON_OK = (stdmsgs.BUTTON_OK[0], 'glyphicon glyphicon-ok')
stdmsgs.BUTTON_APPLY = (stdmsgs.BUTTON_APPLY[0], 'glyphicon glyphicon-cog')
stdmsgs.BUTTON_CANCEL = (stdmsgs.BUTTON_CANCEL[0], 'glyphicon glyphicon-remove')
stdmsgs.BUTTON_DELETE = (stdmsgs.BUTTON_DELETE[0], 'glyphicon glyphicon-trash')


# Override default form buttons to 'btn-class' and use bootstrap glyphicons.
# Keep the `validateButton` as it is used in js (e.g `unfreezeFormButtons`)

formwidgets.Button.css_class = 'btn btn-default validateButton'
formwidgets.SubmitButton.css_class = 'btn btn-primary validateButton'

monkeypatch_default_value(formwidgets.Button.__init__, 'label', (stdmsgs.BUTTON_OK[0], 'glyphicon glyphicon-ok'))
# options #############################################################

options = (
    ('cw_compatibility',
      {'type' : 'yn',
      'default': False,
      'help': 'use compat css rules (enable if your application uses views that have not been ported to bootstrap)',
      'group': 'bootstrap', 'level': 2,
      }),
)
