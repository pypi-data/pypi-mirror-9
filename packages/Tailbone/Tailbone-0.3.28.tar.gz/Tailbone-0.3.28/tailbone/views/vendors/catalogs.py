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
Views for maintaining vendor catalogs
"""

from __future__ import unicode_literals

from rattail.db import model
from rattail.db.api import get_setting, get_vendor
from rattail.db.batch.vendorcatalog import VendorCatalog, VendorCatalogRow
from rattail.db.batch.vendorcatalog.handler import VendorCatalogHandler
from rattail.vendors.catalogs import iter_catalog_parsers, require_catalog_parser
from rattail.util import load_object

import formalchemy

from tailbone.db import Session
from tailbone.views.batch import FileBatchGrid, FileBatchCrud, BatchRowGrid, BatchRowCrud, defaults


class VendorCatalogGrid(FileBatchGrid):
    """
    Grid view for vendor catalogs.
    """
    batch_class = VendorCatalog
    batch_display = "Vendor Catalog"
    route_prefix = 'vendors.catalogs'

    def join_map_extras(self):
        return {'vendor': lambda q: q.join(model.Vendor)}

    def filter_map_extras(self):
        return {'vendor': self.filter_ilike(model.Vendor.name)}

    def filter_config_extras(self):
        return {'filter_type_vendor': 'lk',
                'include_filter_vendor': True}

    def sort_map_extras(self):
        return {'vendor': self.sorter(model.Vendor.name)}

    def configure_grid(self, g):
        g.configure(
            include=[
                g.created,
                g.created_by,
                g.vendor,
                g.effective,
                g.filename,
                g.executed,
                ],
            readonly=True)


class VendorCatalogCrud(FileBatchCrud):
    """
    CRUD view for vendor catalogs.
    """
    batch_class = VendorCatalog
    batch_handler_class = VendorCatalogHandler
    route_prefix = 'vendors.catalogs'

    batch_display = "Vendor Catalog"
    flash = {'create': "New vendor catalog has been uploaded.",
             'delete': "Vendor catalog has been deleted."}

    def get_handler(self):
        """
        Returns a `BatchHandler` instance for the view.

        Derived classes may override this, but if you only need to replace the
        handler (i.e. and not the view logic) then you can instead subclass
        :class:`rattail.db.batch.vendorcatalog.handler.VendorCatalogHandler`
        and create a setting named "rattail.batch.vendorcatalog.handler" in the
        database, the value of which should be a spec string pointed at your
        custom handler.
        """
        handler = get_setting(Session, 'rattail.batch.vendorcatalog.handler')
        if handler:
            handler = load_object(handler)(self.request.rattail_config)
        if not handler:
            handler = super(VendorCatalogCrud, self).get_handler()
        return handler

    def configure_fieldset(self, fs):
        parsers = sorted(iter_catalog_parsers(), key=lambda p: p.display)
        parser_options = [(p.display, p.key) for p in parsers]
        parser_options.insert(0, ("(please choose)", ''))
        fs.parser_key.set(renderer=formalchemy.fields.SelectFieldRenderer,
                          options=parser_options)
        fs.configure(
            include=[
                fs.created,
                fs.created_by,
                fs.vendor,
                fs.data_file.label("Catalog File"),
                fs.filename,
                fs.parser_key.label("File Type"),
                fs.effective,
                fs.executed,
                fs.executed_by,
                ])
        if self.creating:
            del fs.vendor
            del fs.effective
        else:
            del fs.parser_key

    def init_batch(self, batch):
        parser = require_catalog_parser(batch.parser_key)
        batch.vendor = get_vendor(Session, parser.vendor_key)


class VendorCatalogRowGrid(BatchRowGrid):
    """
    Grid view for vendor catalog rows.
    """
    row_class = VendorCatalogRow
    route_prefix = 'vendors.catalogs'

    def filter_map_extras(self):
        return {'ilike': ['upc', 'brand_name', 'description', 'size', 'vendor_code']}

    def filter_config_extras(self):
        return {'filter_label_upc': "UPC",
                'filter_label_brand_name': "Brand"}

    def configure_grid(self, g):
        g.configure(
            include=[
                g.sequence,
                g.upc.label("UPC"),
                g.brand_name.label("Brand"),
                g.description,
                g.size,
                g.vendor_code,
                g.old_unit_cost.label("Old Cost"),
                g.unit_cost.label("New Cost"),
                g.unit_cost_diff.label("Diff."),
                g.status_code,
                ],
            readonly=True)

    def tr_class(self, row, i):
        if row.status_code in (row.STATUS_NEW_COST, row.STATUS_UPDATE_COST):
            return 'notice'
        if row.status_code == row.STATUS_PRODUCT_NOT_FOUND:
            return 'warning'


class VendorCatalogRowCrud(BatchRowCrud):
    row_class = VendorCatalogRow
    route_prefix = 'vendors.catalogs'


def includeme(config):
    defaults(config, VendorCatalogGrid, VendorCatalogCrud, VendorCatalogRowGrid, VendorCatalogRowCrud, '/vendors/catalogs/')
