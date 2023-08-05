#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Core Grid View
"""

from .. import View
from ... import grids


__all__ = ['GridView']


class GridView(View):

    route_name = None
    route_url = None
    renderer = None
    permission = None

    full = False
    checkboxes = False
    deletable = False

    partial_only = False

    def update_grid_kwargs(self, kwargs):
        kwargs.setdefault('full', self.full)
        kwargs.setdefault('checkboxes', self.checkboxes)
        kwargs.setdefault('deletable', self.deletable)
        kwargs.setdefault('partial_only', self.partial_only)

    def make_grid(self, **kwargs):
        self.update_grid_kwargs(kwargs)
        return grids.Grid(self.request, **kwargs)

    def grid(self):
        return self.make_grid()

    def render_kwargs(self):
        return {}

    def __call__(self):
        grid = self.grid()
        kwargs = self.render_kwargs()
        return grids.util.render_grid(grid, **kwargs)
