# -*- coding: utf-8 -*-
# copyright 2014 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-uitest boxes"""
from logilab.mtconverter import xml_escape

from cubicweb.web import component
from cubicweb.web.views import boxes
from cubicweb.web.views.bookmark import BookmarksBox
from cubicweb.utils import wrap_on_write

try:
    from cubes.bootstrap.views.basecomponents import BSRQLInputForm as RQLInputForm
    cube_bootstrap = True
except:
    from cubicweb.web.views.basecomponents import RQLInputForm
    cube_bootstrap = False

LINKS_CONTEXT = 'right'
BookmarksBox.context = LINKS_CONTEXT
boxes.EditBox.context = LINKS_CONTEXT
boxes.context = LINKS_CONTEXT
boxes.PossibleViewsBox.context = LINKS_CONTEXT
boxes.PossibleViewsBox.visible = True
boxes.StartupViewsBox.context = LINKS_CONTEXT
# display the Rql input
RQLInputForm.visible = True

class UiTestLinksBox(component.CtxComponent):
    context = LINKS_CONTEXT

    def render_links(self, links, w):
        _ = self._cw._
        w(u'<ul class="list-unstyled">')
        for title, url in links:
            selected = self._cw.selected(url)
            css = 'class="selected"' if selected else ''
            w(u'<li><a href="%s" %s>%s</a></li>\n' % (xml_escape(url), css, _(title)))
        w(u'</ul>')


class StaticLinksBox(UiTestLinksBox):
    """side box with static links"""
    __regid__ = 'uitest.static_views'
    title = _('static links')
    order = 1

    def render_body(self, w):
        links = [
            ('typography', self._cw.build_url('view', vid='uitest.typography')),
            ('static tables', self._cw.build_url('view', vid='uitest.static_tables')),
            ]
        if cube_bootstrap:
            links.append(('static forms', self._cw.build_url('view', vid='uitest.static_forms')))
        self.render_links(links, w)


class EveryThingLinksBox(UiTestLinksBox):
    """side box with dynamic links"""
    __regid__ = 'uitest.everything_views'
    title = _('EveryThing views')
    order = 2

    def render_body(self, w):
        et_url = self._cw.vreg["etypes"].etype_class('EveryThing').cw_create_url(self._cw)
        links = [
            ('EveryThing edition form', et_url),
            ]
        rset = self._cw.execute('Any X WHERE X is EveryThing')
        if rset:
            entity = rset.get_entity(0,0)
            links.append(('EveryThing primary view', entity.absolute_url()))
            links.append(('EveryThing list view', self._cw.build_url('list', rql=rset.printable_rql())))
            links.append(('EveryThing all views', self._cw.build_url('view', vid='uitest.secondary')))
        self.render_links(links, w)


class DynamicLinksBox(UiTestLinksBox):
    """side box with dynamic links"""
    __regid__ = 'uitest.dynamic_views'
    title = _('dynamic links')
    order = 4

    def render_body(self, w):
        links = (
            ('CWEntities tables', self._cw.build_url('view', vid='uitest.dynamic_tables')),
            ('Jquery tab', self._cw.build_url('cwetype/Date')),
            )
        self.render_links(links, w)
