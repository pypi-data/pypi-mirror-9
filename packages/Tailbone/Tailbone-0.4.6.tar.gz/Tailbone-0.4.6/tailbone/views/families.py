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
Family Views
"""

from . import SearchableAlchemyGridView, CrudView

from rattail.db import model


class FamiliesGrid(SearchableAlchemyGridView):

    mapped_class = model.Family
    config_prefix = 'families'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(
            exact=['code'],
            ilike=['name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk')

    def sort_map(self):
        return self.make_sort_map('code', 'name')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.code,
                g.name,
                ],
            readonly=True)
        if self.request.has_perm('families.read'):
            g.viewable = True
            g.view_route_name = 'family.read'
        if self.request.has_perm('families.update'):
            g.editable = True
            g.edit_route_name = 'family.update'
        if self.request.has_perm('families.delete'):
            g.deletable = True
            g.delete_route_name = 'family.delete'
        return g


class FamilyCrud(CrudView):

    mapped_class = model.Family
    home_route = 'families'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.code,
                fs.name,
                ])
        return fs


def add_routes(config):
    config.add_route('families', '/families')
    config.add_route('family.create', '/families/new')
    config.add_route('family.read', '/families/{uuid}')
    config.add_route('family.update', '/families/{uuid}/edit')
    config.add_route('family.delete', '/families/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(FamiliesGrid, route_name='families',
                    renderer='/families/index.mako',
                    permission='families.list')

    config.add_view(FamilyCrud, attr='create', route_name='family.create',
                    renderer='/families/crud.mako',
                    permission='families.create')
    config.add_view(FamilyCrud, attr='read', route_name='family.read',
                    renderer='/families/crud.mako',
                    permission='families.read')
    config.add_view(FamilyCrud, attr='update', route_name='family.update',
                    renderer='/families/crud.mako',
                    permission='families.update')
    config.add_view(FamilyCrud, attr='delete', route_name='family.delete',
                    permission='families.delete')
