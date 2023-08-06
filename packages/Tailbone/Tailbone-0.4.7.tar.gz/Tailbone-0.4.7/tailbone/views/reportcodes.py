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
Report Code Views
"""

from tailbone.views import SearchableAlchemyGridView, CrudView

from rattail.db import model


class ReportCodesGrid(SearchableAlchemyGridView):

    mapped_class = model.ReportCode
    config_prefix = u'reportcodes'
    sort = u'name'

    def filter_map(self):
        return self.make_filter_map(
            exact=[u'code'],
            ilike=[u'name'])

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name=u'lk')

    def sort_map(self):
        return self.make_sort_map(u'code', u'name')

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.code,
                g.name,
                ],
            readonly=True)
        if self.request.has_perm(u'reportcodes.read'):
            g.viewable = True
            g.view_route_name = u'reportcode.read'
        if self.request.has_perm(u'reportcodes.update'):
            g.editable = True
            g.edit_route_name = u'reportcode.update'
        if self.request.has_perm(u'reportcodes.delete'):
            g.deletable = True
            g.delete_route_name = u'reportcode.delete'
        return g


class ReportCodeCrud(CrudView):

    mapped_class = model.ReportCode
    home_route = u'reportcodes'

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.configure(
            include=[
                fs.code,
                fs.name,
                ])
        return fs


def add_routes(config):
    config.add_route(u'reportcodes', u'/reportcodes')
    config.add_route(u'reportcode.create', u'/reportcodes/new')
    config.add_route(u'reportcode.read', u'/reportcodes/{uuid}')
    config.add_route(u'reportcode.update', u'/reportcodes/{uuid}/edit')
    config.add_route(u'reportcode.delete', u'/reportcodes/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(ReportCodesGrid, route_name=u'reportcodes',
                    renderer=u'/reportcodes/index.mako',
                    permission=u'reportcodes.list')

    config.add_view(ReportCodeCrud, attr=u'create', route_name=u'reportcode.create',
                    renderer=u'/reportcodes/crud.mako',
                    permission=u'reportcodes.create')
    config.add_view(ReportCodeCrud, attr=u'read', route_name=u'reportcode.read',
                    renderer=u'/reportcodes/crud.mako',
                    permission=u'reportcodes.read')
    config.add_view(ReportCodeCrud, attr=u'update', route_name=u'reportcode.update',
                    renderer=u'/reportcodes/crud.mako',
                    permission=u'reportcodes.update')
    config.add_view(ReportCodeCrud, attr=u'delete', route_name=u'reportcode.delete',
                    permission=u'reportcodes.delete')
