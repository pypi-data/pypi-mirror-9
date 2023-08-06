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
Tax Views
"""

from __future__ import unicode_literals

from rattail.db import model

from tailbone.views import SearchableAlchemyGridView, CrudView


class TaxesGrid(SearchableAlchemyGridView):

    mapped_class = model.Tax
    config_prefix = 'taxes'
    sort = 'code'

    def filter_map(self):
        return self.make_filter_map(exact=['code'], ilike=['description'])

    def filter_config(self):
        return self.make_filter_config(include_filter_description=True,
                                       filter_type_description='lk')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.code,
                g.description,
                g.rate,
                ],
            readonly=True)
        if self.request.has_perm('taxes.view'):
            g.viewable = True
            g.view_route_name = 'tax.view'
        if self.request.has_perm('taxes.edit'):
            g.editable = True
            g.edit_route_name = 'tax.edit'
        if self.request.has_perm('taxes.delete'):
            g.deletable = True
            g.delete_route_name = 'tax.delete'
        return g


class TaxCrud(CrudView):

    mapped_class = model.Tax
    home_route = 'taxes'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.code,
                fs.description,
                fs.rate,
                ])
        return fs


def add_routes(config):
    config.add_route('taxes',           '/taxes')
    config.add_route('tax.new',      '/taxes/new')
    config.add_route('tax.view',        '/taxes/{uuid}')
    config.add_route('tax.edit',        '/taxes/{uuid}/edit')
    config.add_route('tax.delete',      '/taxes/{uuid}/delete')


def includeme(config):
    add_routes(config)

    # list taxes
    config.add_view(TaxesGrid, route_name='taxes',
                    renderer='/taxes/index.mako', permission='taxes.list')

    # tax crud
    config.add_view(TaxCrud, attr='create', route_name='tax.new',
                    renderer='/taxes/crud.mako', permission='taxes.create')
    config.add_view(TaxCrud, attr='read', route_name='tax.view',
                    renderer='/taxes/crud.mako', permission='taxes.view')
    config.add_view(TaxCrud, attr='update', route_name='tax.edit',
                    renderer='/taxes/crud.mako', permission='taxes.edit')
    config.add_view(TaxCrud, attr='delete', route_name='tax.delete',
                    permission='taxes.delete')
