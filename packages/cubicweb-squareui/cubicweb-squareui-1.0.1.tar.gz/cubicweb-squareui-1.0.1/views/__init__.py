# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-squareui views/forms/actions/components for web ui"""
from cubicweb.web.views.boxes import ContextualBoxLayout, contextual

_ = unicode

class SimpleBoxContextFreeBoxLayout(ContextualBoxLayout):
    __select__ = ~contextual()
    cssclass = 'contextFreeBox'
    __regid__ = 'simple-layout'

    def render(self, w):
        if self.init_rendering():
            view = self.cw_extra_kwargs['view']
            view.render_body(w)
