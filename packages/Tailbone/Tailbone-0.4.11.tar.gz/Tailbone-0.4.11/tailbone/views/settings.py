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
Settings Views
"""

from __future__ import unicode_literals

from rattail.db import model

from tailbone.views import SearchableAlchemyGridView, CrudView


class SettingsGrid(SearchableAlchemyGridView):

    mapped_class = model.Setting
    config_prefix = 'settings'
    sort = 'name'

    def filter_map(self):
        return self.make_filter_map(ilike=['name', 'value'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk',
            include_filter_value=True,
            filter_type_value='lk')

    def sort_map(self):
        return self.make_sort_map('name', 'value')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.name,
                g.value,
                ],
            readonly=True)
        if self.request.has_perm('settings.view'):
            g.viewable = True
            g.view_route_name = 'settings.view'
        if self.request.has_perm('settings.edit'):
            g.editable = True
            g.edit_route_name = 'settings.edit'
        if self.request.has_perm('settings.delete'):
            g.deletable = True
            g.delete_route_name = 'settings.delete'
        return g


class SettingCrud(CrudView):

    mapped_class = model.Setting
    home_route = 'settings'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.name,
                fs.value,
                ])
        if self.updating:
            fs.name.set(readonly=True)
        return fs
        

def add_routes(config):
    config.add_route('settings',                '/settings')
    config.add_route('settings.create',         '/settings/new')
    config.add_route('settings.view',           '/settings/{name}')
    config.add_route('settings.edit',           '/settings/{name}/edit')
    config.add_route('settings.delete',         '/settings/{name}/delete')


def includeme(config):
    add_routes(config)

    # Grid
    config.add_view(SettingsGrid,
                    route_name='settings',
                    renderer='/settings/index.mako',
                    permission='settings.list')

    # CRUD
    config.add_view(SettingCrud, attr='create',
                    route_name='settings.create',
                    renderer='/settings/crud.mako',
                    permission='settings.create')
    config.add_view(SettingCrud, attr='read',
                    route_name='settings.view',
                    renderer='/settings/crud.mako',
                    permission='settings.view')
    config.add_view(SettingCrud, attr='update',
                    route_name='settings.edit',
                    renderer='/settings/crud.mako',
                    permission='settings.edit')
    config.add_view(SettingCrud, attr='delete',
                    route_name='settings.delete',
                    permission='settings.delete')
