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
FormAlchemy Grid Views
"""

from webhelpers import paginate

from .core import GridView
from ... import grids
from ...db import Session


__all__ = ['AlchemyGridView', 'SortableAlchemyGridView',
           'PagedAlchemyGridView', 'SearchableAlchemyGridView']


class AlchemyGridView(GridView):

    def make_query(self, session=Session):
        query = session.query(self.mapped_class)
        return self.modify_query(query)

    def modify_query(self, query):
        return query

    def query(self):
        return self.make_query()

    def make_grid(self, **kwargs):
        self.update_grid_kwargs(kwargs)
        return grids.AlchemyGrid(
            self.request, self.mapped_class, self._data, **kwargs)

    def grid(self):
        return self.make_grid()

    def __call__(self):
        self._data = self.query()
        grid = self.grid()
        return self.render_grid(grid)


class SortableAlchemyGridView(AlchemyGridView):

    sort = None
    full = True

    @property
    def config_prefix(self):
        raise NotImplementedError

    def join_map(self):
        return {}

    def make_sort_map(self, *args, **kwargs):
        return grids.util.get_sort_map(
            self.mapped_class, names=args or None, **kwargs)

    def sorter(self, field):
        return grids.util.sorter(field)

    def sort_map(self):
        return self.make_sort_map()

    def make_sort_config(self, **kwargs):
        return grids.util.get_sort_config(
            self.config_prefix, self.request, **kwargs)

    def sort_config(self):
        return self.make_sort_config(sort=self.sort)

    def modify_query(self, query):
        return grids.util.sort_query(
            query, self._sort_config, self.sort_map(), self.join_map())

    def make_grid(self, **kwargs):
        self.update_grid_kwargs(kwargs)
        return grids.AlchemyGrid(
            self.request, self.mapped_class, self._data,
            sort_map=self.sort_map(), config=self._sort_config, **kwargs)

    def grid(self):
        return self.make_grid()

    def __call__(self):
        self._sort_config = self.sort_config()
        self._data = self.query()
        grid = self.grid()
        return self.render_grid(grid)


class PagedAlchemyGridView(SortableAlchemyGridView):

    def make_pager(self):
        config = self._sort_config
        query = self.query()
        return paginate.Page(
            query, item_count=query.count(),
            items_per_page=int(config['per_page']),
            page=int(config['page']),
            url=paginate.PageURL_WebOb(self.request))

    def __call__(self):
        self._sort_config = self.sort_config()
        self._data = self.make_pager()
        grid = self.grid()
        grid.pager = self._data
        return self.render_grid(grid)


class SearchableAlchemyGridView(PagedAlchemyGridView):

    def filter_exact(self, field):
        return grids.search.filter_exact(field)

    def filter_ilike(self, field):
        return grids.search.filter_ilike(field)

    def filter_int(self, field):
        return grids.search.filter_int(field)

    def filter_soundex(self, field):
        return grids.search.filter_soundex(field)

    def filter_ilike_and_soundex(self, field):
        return grids.search.filter_ilike_and_soundex(field)

    def filter_gpc(self, field):
        return grids.search.filter_gpc(field)

    def make_filter_map(self, **kwargs):
        return grids.search.get_filter_map(self.mapped_class, **kwargs)

    def filter_map(self):
        return self.make_filter_map()

    def make_filter_config(self, **kwargs):
        return grids.search.get_filter_config(
            self.config_prefix, self.request, self.filter_map(), **kwargs)

    def filter_config(self):
        return self.make_filter_config()

    def make_search_form(self):
        return grids.search.get_search_form(
            self.request, self.filter_map(), self._filter_config)

    def search_form(self):
        return self.make_search_form()

    def modify_query(self, query):
        join_map = self.join_map()
        if not hasattr(self, '_filter_config'):
            self._filter_config = self.filter_config()
        query = grids.search.filter_query(
            query, self._filter_config, self.filter_map(), join_map)
        if hasattr(self, '_sort_config'):
            self._sort_config['joins'] = self._filter_config['joins']
            query = grids.util.sort_query(
                query, self._sort_config, self.sort_map(), join_map)
        return query

    def __call__(self):
        self._filter_config = self.filter_config()
        search = self.search_form()
        self._sort_config = self.sort_config()
        self._data = self.make_pager()
        grid = self.grid()
        grid.pager = self._data
        return self.render_grid(grid, search)
