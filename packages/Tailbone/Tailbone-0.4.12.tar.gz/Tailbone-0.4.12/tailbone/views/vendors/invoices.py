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
Views for maintaining vendor invoices
"""

from __future__ import unicode_literals

from rattail.db import model
from rattail.db.api import get_setting, get_vendor
from rattail.db.batch.vendorinvoice import VendorInvoice, VendorInvoiceRow
from rattail.db.batch.vendorinvoice.handler import VendorInvoiceHandler
from rattail.vendors.invoices import iter_invoice_parsers, require_invoice_parser
from rattail.util import load_object

import formalchemy

from tailbone.db import Session
from tailbone.views.batch import FileBatchGrid, FileBatchCrud, BatchRowGrid, BatchRowCrud, defaults


class VendorInvoiceGrid(FileBatchGrid):
    """
    Grid view for vendor invoices.
    """
    batch_class = VendorInvoice
    batch_display = "Vendor Invoice"
    route_prefix = 'vendors.invoices'

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
                g.filename,
                g.executed,
                ],
            readonly=True)


class VendorInvoiceCrud(FileBatchCrud):
    """
    CRUD view for vendor invoices.
    """
    batch_class = VendorInvoice
    batch_handler_class = VendorInvoiceHandler
    route_prefix = 'vendors.invoices'

    batch_display = "Vendor Invoice"
    flash = {'create': "New vendor invoice has been uploaded.",
             'update': "Vendor invoice has been updated.",
             'delete': "Vendor invoice has been deleted."}

    def get_handler(self):
        """
        Returns a `BatchHandler` instance for the view.

        Derived classes may override this, but if you only need to replace the
        handler (i.e. and not the view logic) then you can instead subclass
        :class:`rattail.db.batch.vendorinvoice.handler.VendorInvoiceHandler`
        and create a setting named "rattail.batch.vendorinvoice.handler" in the
        database, the value of which should be a spec string pointed at your
        custom handler.
        """
        handler = get_setting(Session, 'rattail.batch.vendorinvoice.handler')
        if not handler:
            handler = self.request.rattail_config.get('rattail.batch', 'vendorinvoice.handler')
        if handler:
            handler = load_object(handler)(self.request.rattail_config)
        if not handler:
            handler = super(VendorInvoiceCrud, self).get_handler()
        return handler

    def validate_po_number(self, value, field):
        """
        Let the invoice handler in effect determine if the user-provided
        purchase order number is valid.
        """
        parser_key = field.parent.parser_key.value
        if not parser_key:
            raise formalchemy.ValidationError("Cannot validate PO number until File Type is chosen")
        parser = require_invoice_parser(parser_key)
        vendor = get_vendor(Session(), parser.vendor_key)
        try:
            self.handler.validate_po_number(value, vendor)
        except ValueError as error:
            raise formalchemy.ValidationError(unicode(error))

    def configure_fieldset(self, fs):
        parsers = sorted(iter_invoice_parsers(), key=lambda p: p.display)
        parser_options = [(p.display, p.key) for p in parsers]
        parser_options.insert(0, ("(please choose)", ''))
        fs.parser_key.set(renderer=formalchemy.fields.SelectFieldRenderer,
                          options=parser_options)

        fs.purchase_order_number.set(label=self.handler.po_number_title)
        fs.purchase_order_number.set(validate=self.validate_po_number)

        fs.configure(
            include=[
                fs.vendor.readonly(),
                fs.filename.label("Invoice File"),
                fs.parser_key.label("File Type"),
                fs.purchase_order_number,
                fs.invoice_date.readonly(),
                fs.created,
                fs.created_by,
                fs.executed,
                fs.executed_by,
                ])
        if self.creating:
            del fs.vendor
            del fs.invoice_date
        else:
            del fs.parser_key

    def init_batch(self, batch):
        parser = require_invoice_parser(batch.parser_key)
        vendor = get_vendor(Session, parser.vendor_key)
        if not vendor:
            self.request.session.flash("No vendor setting found in database for key: {0}".format(parser.vendor_key))
            return False
        batch.vendor = vendor
        return True


class VendorInvoiceRowGrid(BatchRowGrid):
    """
    Grid view for vendor invoice rows.
    """
    row_class = VendorInvoiceRow
    route_prefix = 'vendors.invoices'

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
                g.shipped_cases.label("Cases"),
                g.shipped_units.label("Units"),
                g.unit_cost,
                g.status_code,
                ],
            readonly=True)

    def tr_class(self, row, i):
        if row.status_code in ((row.STATUS_NOT_IN_PURCHASE,
                                row.STATUS_NOT_IN_INVOICE,
                                row.STATUS_DIFFERS_FROM_PURCHASE)):
            return 'notice'
        if row.status_code in (row.STATUS_NOT_IN_DB,
                               row.STATUS_COST_NOT_IN_DB):
            return 'warning'


class VendorInvoiceRowCrud(BatchRowCrud):
    row_class = VendorInvoiceRow
    route_prefix = 'vendors.invoices'
    batch_display = "Vendor Invoice"


def includeme(config):
    """
    Add configuration for the vendor invoice views.
    """
    defaults(config, VendorInvoiceGrid, VendorInvoiceCrud, VendorInvoiceRowGrid, VendorInvoiceRowCrud, '/vendors/invoices/')
