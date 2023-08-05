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

from logilab.common.registry import yes

from cubicweb.web.views.basecomponents import HeaderComponent
from cubicweb.web.views.basetemplates import TheMainTemplate


class HideAsidesBar(HeaderComponent):
    """ Hide the left bar """
    __regid__ = 'hide-left-bar'
    __select__ = yes()
    context = 'header-right'
    order = 3
    visible = False
    icon_css_cls = 'glyphicon glyphicon-align-justify'

    def render(self, w):
        define_var = self._cw.html_headers.define_var
        define_var('twbs_col_cls', TheMainTemplate.twbs_col_cls)
        define_var('twbs_col_size', TheMainTemplate.twbs_col_size)
        define_var('twbs_grid_columns', TheMainTemplate.twbs_grid_columns)
        w(u'''<button class="btn btn-default navbar-btn" id="cw-aside-toggle"
              onclick="cw.cubes.squareui.toggleLeftColumn()" title="%(label)s">
              <span class="%(icon_class)s"></span>
              </button>''' % {
                'icon_class': self.icon_css_cls,
                'label': self._cw._('collapse boxes')
              })
