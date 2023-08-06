# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
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
Deposit Link Views
"""

from __future__ import unicode_literals

from rattail.db import model

from tailbone.views import SearchableAlchemyGridView, CrudView


class DepositLinksGrid(SearchableAlchemyGridView):

    mapped_class = model.DepositLink
    config_prefix = 'depositlinks'
    sort = 'code'

    def filter_map(self):
        return self.make_filter_map(exact=['code', 'amount'],
                                    ilike=['description'])

    def filter_config(self):
        return self.make_filter_config(include_filter_description=True,
                                       filter_type_description='lk')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.code,
                g.description,
                g.amount,
                ],
            readonly=True)
        if self.request.has_perm('depositlinks.view'):
            g.viewable = True
            g.view_route_name = 'depositlink.view'
        if self.request.has_perm('depositlinks.edit'):
            g.editable = True
            g.edit_route_name = 'depositlink.edit'
        if self.request.has_perm('depositlinks.delete'):
            g.deletable = True
            g.delete_route_name = 'depositlink.delete'
        return g


class DepositLinkCrud(CrudView):

    mapped_class = model.DepositLink
    home_route = 'depositlinks'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.code,
                fs.description,
                fs.amount,
                ])
        return fs


def add_routes(config):
    config.add_route('depositlinks',            '/depositlinks')
    config.add_route('depositlink.new',         '/depositlinks/new')
    config.add_route('depositlink.view',        '/depositlinks/{uuid}')
    config.add_route('depositlink.edit',        '/depositlinks/{uuid}/edit')
    config.add_route('depositlink.delete',      '/depositlinks/{uuid}/delete')


def includeme(config):
    add_routes(config)

    # list deposit links
    config.add_view(DepositLinksGrid, route_name='depositlinks',
                    renderer='/depositlinks/index.mako', permission='depositlinks.list')

    # deposit link crud
    config.add_view(DepositLinkCrud, attr='create', route_name='depositlink.new',
                    renderer='/depositlinks/crud.mako', permission='depositlinks.create')
    config.add_view(DepositLinkCrud, attr='read', route_name='depositlink.view',
                    renderer='/depositlinks/crud.mako', permission='depositlinks.view')
    config.add_view(DepositLinkCrud, attr='update', route_name='depositlink.edit',
                    renderer='/depositlinks/crud.mako', permission='depositlinks.edit')
    config.add_view(DepositLinkCrud, attr='delete', route_name='depositlink.delete',
                    permission='depositlinks.delete')
