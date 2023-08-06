# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2014 Lance Edgar
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
FormAlchemy Grid Classes
"""

from __future__ import unicode_literals

from sqlalchemy.orm import object_session

try:
    from sqlalchemy.inspection import inspect
except ImportError:
    inspect = None
    from sqlalchemy.orm import class_mapper

from webhelpers.html import tags
from webhelpers.html import HTML

import formalchemy

import edbob
from edbob.util import prettify

from .core import Grid
from ..db import Session

__all__ = ['AlchemyGrid']


class AlchemyGrid(Grid):

    sort_map = {}

    pager = None
    pager_format = '$link_first $link_previous ~1~ $link_next $link_last'

    def __init__(self, request, cls, instances, **kwargs):
        super(AlchemyGrid, self).__init__(request, **kwargs)
        self._formalchemy_grid = formalchemy.Grid(
            cls, instances, session=Session(), request=request)
        self._formalchemy_grid.prettify = prettify

    def __delattr__(self, attr):
        delattr(self._formalchemy_grid, attr)

    def __getattr__(self, attr):
        return getattr(self._formalchemy_grid, attr)

    def cell_class(self, field):
        classes = [field.name]
        return ' '.join(classes)

    def checkbox(self, row):
        return tags.checkbox('check-'+row.uuid)

    def column_header(self, field):
        class_ = None
        label = field.label()
        if field.key in self.sort_map:
            class_ = 'sortable'
            if field.key == self.config['sort']:
                class_ += ' sorted ' + self.config['dir']
            label = tags.link_to(label, '#')
        return HTML.tag('th', class_=class_, field=field.key,
                        title=self.column_titles.get(field.key), c=label)

    def crud_route_kwargs(self, row):
        if inspect:
            mapper = inspect(row.__class__)
        else:
            mapper = class_mapper(row.__class__)
        keys = [k.key for k in mapper.primary_key]
        values = [getattr(row, k) for k in keys]
        return dict(zip(keys, values))

    view_route_kwargs = crud_route_kwargs
    edit_route_kwargs = crud_route_kwargs
    delete_route_kwargs = crud_route_kwargs

    def iter_fields(self):
        return self._formalchemy_grid.render_fields.itervalues()

    def iter_rows(self):
        for row in self._formalchemy_grid.rows:
            self._formalchemy_grid._set_active(row, object_session(row))
            yield row

    def page_count_options(self):
        options = edbob.config.get('edbob.pyramid', 'grid.page_count_options')
        if options:
            options = options.split(',')
            options = [int(x.strip()) for x in options]
        else:
            options = [5, 10, 20, 50, 100]
        return options

    def page_links(self):
        return self.pager.pager(self.pager_format,
                                symbol_next='next',
                                symbol_previous='prev',
                                onclick="grid_navigate_page(this, '$partial_url'); return false;")

    def render_field(self, field):
        if self._formalchemy_grid.readonly:
            return field.render_readonly()
        return field.render()

    def row_attrs(self, row, i):
        attrs = super(AlchemyGrid, self).row_attrs(row, i)
        if hasattr(row, 'uuid'):
            attrs['uuid'] = row.uuid
        return attrs
