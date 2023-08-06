"""
:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

from logilab.common.decorators import monkeypatch

from cubicweb import view as cwview
from cubicweb.schema import display_name
from cubicweb.web.views.basetemplates import HTMLHeader

# do not wrap cell_calls with <div class="section">

cwview.View.add_div_section = False

@monkeypatch(cwview.View)
def field(self, label, value, row=True, show_label=True, w=None, tr=True,
          table=False):
    """read-only field"""
    if w is None:
        w = self.w
    w(u'<tr>')
    if show_label and label:
        if tr:
            label = display_name(self._cw, label)
        w(u'<th>%s</th>' % label)
    if not (show_label and label):
        w(u'<td colspan="2">%s</td>' % value)
    else:
        w(u'<td>%s</td>' % value)
    w(u'</tr>')

class BSHTMLHeader(HTMLHeader):

    def stylesheets(self):
        super(BSHTMLHeader, self).stylesheets()
        # add cw compatibility stylesheets
        if self._cw.vreg.config['cw_compatibility']:
            for css in self._cw.uiprops['CW_COMPAT_STYLESHEETS']:
                self._cw.add_css(css, localfile=False)

def registration_callback(vreg):
    components = (
        (BSHTMLHeader, HTMLHeader),
        )
    vreg.register_all(globals().values(), __name__,
                      [new for (new, old) in components])
    for new, old in components:
        vreg.register_and_replace(new, old)
