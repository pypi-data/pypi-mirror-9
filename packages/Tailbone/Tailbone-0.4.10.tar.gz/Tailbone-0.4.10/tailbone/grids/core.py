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
Core Grid Classes
"""

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from webhelpers.html import HTML
from webhelpers.html.builder import format_attrs

from pyramid.renderers import render

from rattail.core import Object


__all__ = ['Grid']


class Grid(Object):

    full = False
    hoverable = True
    checkboxes = False
    partial_only = False

    viewable = False
    view_route_name = None
    view_route_kwargs = None

    editable = False
    edit_route_name = None
    edit_route_kwargs = None

    deletable = False
    delete_route_name = None
    delete_route_kwargs = None

    # Set this to a callable to allow ad-hoc row class additions.
    extra_row_class = None

    def __init__(self, request, **kwargs):
        kwargs.setdefault('fields', OrderedDict())
        kwargs.setdefault('column_titles', {})
        kwargs.setdefault('extra_columns', [])
        super(Grid, self).__init__(**kwargs)
        self.request = request

    def add_column(self, name, label, callback):
        self.extra_columns.append(
            Object(name=name, label=label, callback=callback))

    def column_header(self, field):
        return HTML.tag('th', field=field.name,
                        title=self.column_titles.get(field.name),
                        c=field.label)

    def div_attrs(self):
        classes = ['grid']
        if self.full:
            classes.append('full')
        if self.hoverable:
            classes.append('hoverable')
        return format_attrs(
            class_=' '.join(classes),
            url=self.request.current_route_url(_query=None))

    def get_view_url(self, row):
        kwargs = {}
        if self.view_route_kwargs:
            if callable(self.view_route_kwargs):
                kwargs = self.view_route_kwargs(row)
            else:
                kwargs = self.view_route_kwargs
        return self.request.route_url(self.view_route_name, **kwargs)

    def get_edit_url(self, row):
        kwargs = {}
        if self.edit_route_kwargs:
            if callable(self.edit_route_kwargs):
                kwargs = self.edit_route_kwargs(row)
            else:
                kwargs = self.edit_route_kwargs
        return self.request.route_url(self.edit_route_name, **kwargs)

    def get_delete_url(self, row):
        kwargs = {}
        if self.delete_route_kwargs:
            if callable(self.delete_route_kwargs):
                kwargs = self.delete_route_kwargs(row)
            else:
                kwargs = self.delete_route_kwargs
        return self.request.route_url(self.delete_route_name, **kwargs)

    def get_row_attrs(self, row, i):
        attrs = self.row_attrs(row, i)
        return format_attrs(**attrs)

    def row_attrs(self, row, i):
        return {'class_': self.get_row_class(row, i)}

    def get_row_class(self, row, i):
        class_ = self.default_row_class(row, i)
        if callable(self.extra_row_class):
            extra = self.extra_row_class(row, i)
            if extra:
                class_ = '{0} {1}'.format(class_, extra)
        return class_

    def default_row_class(self, row, i):
        return 'odd' if i % 2 else 'even'

    def iter_fields(self):
        return self.fields.itervalues()

    def iter_rows(self):
        """
        Iterate over the grid rows.  The default implementation simply returns
        an iterator over ``self.rows``; note however that by default there is
        no such attribute.  You must either populate that, or overrirde this
        method.
        """
        return iter(self.rows)

    def render(self, template='/grids/grid.mako', **kwargs):
        kwargs.setdefault('grid', self)
        return render(template, kwargs)

    def render_field(self, field):
        raise NotImplementedError
