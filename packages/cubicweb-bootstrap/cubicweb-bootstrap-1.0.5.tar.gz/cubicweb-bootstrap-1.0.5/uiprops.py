"""
:copyright 2012 CreaLibre (Monterrey, MEXICO), all rights reserved.
:contact http://www.crealibre.com/ -- mailto:info@crealibre.com

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

STYLESHEETS = [data('css/bootstrap.min.css'),
               data('cubes.bootstrap.css'),
               data('cubicweb.pictograms.css'),
               ]
CW_COMPAT_STYLESHEETS = [data('cubes.bootstrap.cw_compat.css'),
                         ]

JAVASCRIPTS.extend((data('js/bootstrap.min.js'),
                   data('cubes.bootstrap.js')))
