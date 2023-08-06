"""bootstrap implementation of base templates

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from logilab.mtconverter import xml_escape

from cubicweb.schema import display_name
from cubicweb.utils import UStringIO

from cubicweb.web.views import basetemplates, \
     basecomponents, actions

from cubicweb.web.views.boxes import SearchBox

HTML5 = u'<!DOCTYPE html>'

basetemplates.TheMainTemplate.doctype = HTML5

# options which can be changed freely
basetemplates.TheMainTemplate.twbs_container_cls = 'container-fluid'
basetemplates.TheMainTemplate.twbs_col_cls = 'col-xs-'
basetemplates.TheMainTemplate.twbs_col_size = 2

# options which require recompiling bootstrap.css from source
basetemplates.TheMainTemplate.twbs_grid_columns = 12


@monkeypatch(basetemplates.TheMainTemplate)
def call(self, view):
    self.set_request_content_type()
    self.template_header(self.content_type, view)
    self.template_page_content(view)

@monkeypatch(basetemplates.TheMainTemplate)
def template_header(self, content_type, view=None, page_title='', additional_headers=()):
    page_title = page_title or view.page_title()
    additional_headers = additional_headers or view.html_headers()
    self.template_html_header(content_type, page_title, additional_headers)

@monkeypatch(basetemplates.TheMainTemplate)
def template_html_header(self, content_type, page_title,
                         additional_headers=()):
    w = self.whead
    lang = self._cw.lang
    self.write_doctype()
    self._cw.html_headers.define_var('BASE_URL', self._cw.base_url())
    self._cw.html_headers.define_var('DATA_URL', self._cw.datadir_url)
    w(u'<meta http-equiv="content-type" content="%s; charset=%s"/>\n'
      % (content_type, self._cw.encoding))
    w(u'<meta name="viewport" content="initial-scale=1.0; '
      u'maximum-scale=1.0; width=device-width; "/>')
    w(u'\n'.join(additional_headers) + u'\n')
    self.wview('htmlheader', rset=self.cw_rset)
    if page_title:
        w(u'<title>%s</title>\n' % xml_escape(page_title))

@monkeypatch(basetemplates.TheMainTemplate)
def template_page_content(self, view):
    w = self.w
    self.w(u'<body>\n')
    self.wview('header', rset=self.cw_rset, view=view)
    w(u'<div id="page" class="%s">\n' % self.twbs_container_cls)
    w(u'<div class="row">\n')
    left_boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context='left'))
    right_boxes = list(self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context='right'))
    nb_boxes = int(bool(left_boxes)) + int(bool(right_boxes))
    content_cols = self.twbs_grid_columns
    if nb_boxes:
        content_cols = self.twbs_grid_columns - self.twbs_col_size * nb_boxes
    self.nav_column(view, left_boxes, 'left')
    self.content_column(view, content_cols)
    self.nav_column(view, right_boxes, 'right')
    self.w(u'</div>\n') # closes class=row
    self.w(u'</div>\n') # closes id="page" from template_page_content
    self.template_footer(view)
    self.w(u'</body>\n')

@monkeypatch(basetemplates.TheMainTemplate)
def get_components(self, view, context):
    ctxcomponents = self._cw.vreg['ctxcomponents']
    return ctxcomponents.poss_visible_objects(self._cw,
                                              rset=self.cw_rset,
                                              view=view,
                                              context=context)
@monkeypatch(basetemplates.TheMainTemplate)
def state_header(self):
    state = self._cw.search_state
    if state[0] == 'normal':
        return
    _ = self._cw._
    value = self._cw.view('oneline', self._cw.eid_rset(state[1][1]))
    target, eid, r_type, searched_type = self._cw.search_state[1]
    cancel_link = u'<a href="%(url)s" role="button" class="btn btn-default" title="%(title)s">%(title)s</a>' % {
        'url' : self._cw.build_url(str(eid),
                                   vid='edition', __mode='normal'),
        'title': _('cancel')}
    msg = ' '.join((_("searching for"),
                    '<strong>"%s"</strong>' % \
                    display_name(self._cw, state[1][3]),
                    _("to associate with"), value,
                    _("by relation"),
                    '<strong>"%s"</strong>' % \
                    display_name(self._cw, state[1][2], state[1][0]),
                    cancel_link))
    return self.w(u'<div class="alert alert-info">%s</div>' % msg)

@monkeypatch(basetemplates.TheMainTemplate)
def nav_column(self, view, boxes, context):
    if boxes:
        stream = UStringIO()
        for box in boxes:
            box.render(w=stream.write, view=view)
        html = stream.getvalue()
        if html:
            # only display aside columns if html availble
            self.w(u'<aside id="aside-main-%s" class="%s%s cwjs-aside">\n' %
                   (context, self.twbs_col_cls, self.twbs_col_size))
            self.w(html)
            self.w(u'</aside>\n')
    return len(boxes)

@monkeypatch(basetemplates.TheMainTemplate)
def content_column(self, view, content_cols):
    w = self.w
    w(u'<div id="main-center" class="%(prefix)s%(col)s" role="main">' % {
        'prefix': self.twbs_col_cls, 'col': content_cols})
    components = self._cw.vreg['components']
    self.content_components(view, components)
    w(u'<div id="pageContent">')
    self.content_header(view)
    vtitle = self._cw.form.get('vtitle')
    if vtitle:
        w(u'<div class="vtitle">%s</div>\n' % xml_escape(vtitle))
    self.state_header()
    self.content_navrestriction_components(view, components)
    nav_html = UStringIO()
    if view and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    w(nav_html.getvalue())
    w(u'<div id="contentmain">\n')
    view.render(w=w)
    w(u'</div>\n') # closes id=contentmain
    w(nav_html.getvalue())
    self.content_footer(view)
    w(u'</div>\n') # closes div#pageContent
    w(u'</div>\n') # closes div.%(prefix)s-%(col)s


@monkeypatch(basetemplates.TheMainTemplate)
def content_components(self, view, components):
    """TODO : should use context"""
    rqlcomp = components.select_or_none('rqlinput', self._cw, rset=self.cw_rset)
    if rqlcomp:
        rqlcomp.render(w=self.w, view=view)
    msgcomp = components.select_or_none('applmessages', self._cw, rset=self.cw_rset)
    if msgcomp:
        msgcomp.render(w=self.w)

@monkeypatch(basetemplates.TheMainTemplate)
def content_navrestriction_components(self, view, components):
    # display entity type restriction component
    etypefilter = components.select_or_none(
        'etypenavigation', self._cw, rset=self.cw_rset)
    if etypefilter and etypefilter.cw_propval('visible'):
        etypefilter.render(w=self.w)

@monkeypatch(basetemplates.TheMainTemplate)
def template_footer(self, view=None):
    self.wview('footer', rset=self.cw_rset)

# main header

basecomponents.ApplLogo.context = 'header-logo'
# use basecomponents.ApplicationName.visible = False
basecomponents.ApplicationName.context = 'header-left'
basecomponents.ApplLogo.order = 1
basecomponents.ApplicationName.order = 10
basecomponents.CookieLoginComponent.order = 10
basecomponents.AuthenticatedUserStatus.order = 5
SearchBox.order = -1
SearchBox.context = 'header-right'
SearchBox.layout_id = 'simple-layout'


@monkeypatch(basetemplates.HTMLPageHeader)
def call(self, view, **kwargs):
    self.main_header(view)
    self.breadcrumbs(view)

def get_components(self, view, context):
    ctxcomponents = self._cw.vreg['ctxcomponents']
    return ctxcomponents.poss_visible_objects(self._cw,
                                              rset=self.cw_rset,
                                              view=view,
                                              context=context)

basetemplates.HTMLPageHeader.get_components = get_components
basetemplates.HTMLPageHeader.css = {
    'navbar-extra':  'navbar-default',
    'breadcrumbs':   'cw-breadcrumb',
    'container-cls': basetemplates.TheMainTemplate.twbs_container_cls,
    'header-left':   '',
    'header-right':  'navbar-right',
}

@monkeypatch(basetemplates.HTMLPageHeader)
def main_header(self, view):
    w = self.w
    w(u'<nav class="navbar %s" role="banner">' % self.css['navbar-extra'])
    w(u'<div class="%s">' % self.css['container-cls'])
    self.display_navbar_header(w, view)
    w(u'<div id="tools-group" class="collapse navbar-collapse">')
    self.display_header_components(w, view, 'header-left')
    self.display_header_components(w, view, 'header-right')
    w(u'</div></div></nav>')

def display_navbar_header(self, w, view):
    w(u'''<div class="navbar-header">
    <button class="navbar-toggle" data-target="#tools-group" data-toggle="collapse" type="button">
    <span class="sr-only">%(toggle_label)s</span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    <span class="icon-bar"></span>
    </button>''' % {'toggle_label':self._cw._('Toggle navigation')})
    components = self.get_components(view, context='header-logo')
    if components:
        for component in components:
            component.render(w=w)
    w(u'</div>')

basetemplates.HTMLPageHeader.display_navbar_header = display_navbar_header

def display_header_components(self, w, view, context):
    components = self.get_components(view, context=context)
    if components:
        w(u'<ul class="nav navbar-nav %s">' % self.css[context])
        for component in components:
            w(u'<li>')
            component.render(w=w)
            w(u'</li>')
        w(u'</ul>')

basetemplates.HTMLPageHeader.display_header_components = display_header_components

@monkeypatch(basetemplates.HTMLPageHeader)
def breadcrumbs(self, view):
    components = self.get_components(view, context='header-center')
    if components:
        self.w(u'<nav role="navigation" class="%s">' %
            self.css.get('breadcrumbs', 'breadcrumbs-defaul'))
        for component in components:
            component.render(w=self.w)
        self.w(u'</nav>')


@monkeypatch(basetemplates.HTMLContentFooter)
def call(self, view, **kwargs):
    components = self._cw.vreg['ctxcomponents'].poss_visible_objects(
        self._cw, rset=self.cw_rset, view=view, context='navbottom')
    if components:
        # the row is needed here to correctly put the HTML flux
        self.w(u'<div id="contentfooter">')
        for comp in components:
            comp.render(w=self.w, view=view)
        self.w(u'</div>')

@monkeypatch(basetemplates.HTMLPageFooter)
def call(self, **kwargs):
    self.w(u'<footer id="pagefooter" role="contentinfo">')
    self.footer_content()
    self.w(u'</footer>\n')

def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    vreg.unregister(actions.CancelSelectAction)
