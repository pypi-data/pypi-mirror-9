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
Product Views
"""

from __future__ import unicode_literals

import os
import re

from sqlalchemy import and_
from sqlalchemy.orm import joinedload, aliased

import formalchemy
from webhelpers.html.tags import link_to
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render_to_response

import rattail.labels
from rattail import enum
from rattail import sil
from rattail import batches
from rattail.threads import Thread
from rattail.exceptions import LabelPrintingError
from rattail.db import model
from rattail.db.model import (
    Product, ProductPrice, ProductCost, ProductCode,
    Brand, Vendor, Department, Subdepartment, LabelProfile)
from rattail.gpc import GPC
from rattail.db.api import get_product_by_upc
from rattail.db.util import configure_session
from rattail.pod import get_image_url, get_image_path

from tailbone.views import SearchableAlchemyGridView, CrudView
from tailbone.views.continuum import VersionView, version_defaults
from tailbone.forms import EnumFieldRenderer, DateTimeFieldRenderer
from tailbone.db import Session
from tailbone.forms import GPCFieldRenderer, BrandFieldRenderer, PriceFieldRenderer
from tailbone.forms.renderers import products as forms
from tailbone.progress import SessionProgress


class ProductsGrid(SearchableAlchemyGridView):

    mapped_class = Product
    config_prefix = 'products'
    sort = 'description'

    # These aliases enable the grid queries to filter products which may be
    # purchased from *any* vendor, and yet sort by only the "preferred" vendor
    # (since that's what shows up in the grid column).
    ProductCostAny = aliased(ProductCost)
    VendorAny = aliased(Vendor)

    def join_map(self):

        def join_vendor(q):
            q = q.outerjoin(
                ProductCost,
                and_(
                    ProductCost.product_uuid == Product.uuid,
                    ProductCost.preference == 1,
                    ))
            q = q.outerjoin(Vendor)
            return q

        def join_vendor_any(q):
            q = q.outerjoin(
                self.ProductCostAny,
                self.ProductCostAny.product_uuid == Product.uuid)
            q = q.outerjoin(
                self.VendorAny,
                self.VendorAny.uuid == self.ProductCostAny.vendor_uuid)
            return q

        return {
            'brand':
                lambda q: q.outerjoin(Brand),
            'family':
                lambda q: q.outerjoin(model.Family),
            'department':
                lambda q: q.outerjoin(Department,
                                      Department.uuid == Product.department_uuid),
            'subdepartment':
                lambda q: q.outerjoin(Subdepartment,
                                      Subdepartment.uuid == Product.subdepartment_uuid),
            u'report_code':
                lambda q: q.outerjoin(model.ReportCode),
            'regular_price':
                lambda q: q.outerjoin(ProductPrice,
                                      ProductPrice.uuid == Product.regular_price_uuid),
            'current_price':
                lambda q: q.outerjoin(ProductPrice,
                                      ProductPrice.uuid == Product.current_price_uuid),
            'vendor':
                join_vendor,
            'vendor_any':
                join_vendor_any,
            'code':
                lambda q: q.outerjoin(ProductCode),
            }

    def filter_map(self):
        return self.make_filter_map(
            ilike=['description', 'size'],
            upc=self.filter_gpc(model.Product.upc),
            brand=self.filter_ilike(Brand.name),
            family=self.filter_ilike(model.Family.name),
            department=self.filter_ilike(Department.name),
            report_code=self.filter_ilike(model.ReportCode.name),
            subdepartment=self.filter_ilike(Subdepartment.name),
            vendor=self.filter_ilike(Vendor.name),
            vendor_any=self.filter_ilike(self.VendorAny.name),
            code=self.filter_ilike(ProductCode.code))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_upc=True,
            filter_type_upc='is',
            filter_label_upc="UPC",
            include_filter_brand=True,
            filter_type_brand='lk',
            include_filter_description=True,
            filter_type_description='lk',
            include_filter_department=True,
            filter_type_department='lk',
            filter_label_vendor="Vendor (preferred)",
            include_filter_vendor_any=True,
            filter_label_vendor_any="Vendor (any)",
            filter_type_vendor_any='lk')

    def sort_map(self):
        return self.make_sort_map(
            'upc', 'description', 'size',
            brand=self.sorter(Brand.name),
            department=self.sorter(Department.name),
            subdepartment=self.sorter(Subdepartment.name),
            regular_price=self.sorter(ProductPrice.price),
            current_price=self.sorter(ProductPrice.price),
            vendor=self.sorter(Vendor.name))

    def query(self):
        q = self.make_query()
        if not self.request.has_perm('products.view_deleted'):
            q = q.filter(model.Product.deleted == False)
        q = q.options(joinedload(Product.brand))
        q = q.options(joinedload(Product.department))
        q = q.options(joinedload(Product.subdepartment))
        q = q.options(joinedload(Product.regular_price))
        q = q.options(joinedload(Product.current_price))
        q = q.options(joinedload(Product.vendor))
        return q

    def grid(self):
        def extra_row_class(row, i):
            cls = []
            if row.not_for_sale:
                cls.append('not-for-sale')
            if row.deleted:
                cls.append('deleted')
            return ' '.join(cls) if cls else None
        g = self.make_grid(extra_row_class=extra_row_class)
        g.upc.set(renderer=GPCFieldRenderer)
        g.regular_price.set(renderer=PriceFieldRenderer)
        g.current_price.set(renderer=PriceFieldRenderer)
        g.configure(
            include=[
                g.upc.label("UPC"),
                g.brand,
                g.description,
                g.size,
                g.subdepartment,
                g.vendor.label("Pref. Vendor"),
                g.regular_price.label("Reg. Price"),
                g.current_price.label("Cur. Price"),
                ],
            readonly=True)

        if self.request.has_perm('products.read'):
            g.viewable = True
            g.view_route_name = 'product.read'
        if self.request.has_perm('products.update'):
            g.editable = True
            g.edit_route_name = 'product.update'
        if self.request.has_perm('products.delete'):
            g.deletable = True
            g.delete_route_name = 'product.delete'

        # Maybe add Print Label column.
        if self.request.rattail_config.getboolean('tailbone', 'products.print_labels', default=True):
            q = Session.query(LabelProfile)
            if q.count():
                def labels(row):
                    return link_to("Print", '#', class_='print-label')
                g.add_column('labels', "Labels", labels)

        return g

    def render_kwargs(self):
        q = Session.query(LabelProfile)
        q = q.filter(LabelProfile.visible == True)
        q = q.order_by(LabelProfile.ordinal)
        return {'label_profiles': q.all()}


class ProductCrud(CrudView):
    """
    Product CRUD view class.
    """
    mapped_class = Product
    home_route = 'products'
    child_version_classes = [
        (model.ProductCode, 'product_uuid'),
        (model.ProductCost, 'product_uuid'),
        (model.ProductPrice, 'product_uuid'),
        ]

    def get_model(self, key):
        model = super(ProductCrud, self).get_model(key)
        if model:
            return model
        model = Session.query(ProductPrice).get(key)
        if model:
            return model.product
        return None

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.upc.set(renderer=GPCFieldRenderer)
        fs.brand.set(options=[])
        fs.unit_of_measure.set(renderer=EnumFieldRenderer(enum.UNIT_OF_MEASURE))
        fs.regular_price.set(renderer=PriceFieldRenderer)
        fs.current_price.set(renderer=PriceFieldRenderer)

        fs.append(formalchemy.Field('current_price_ends'))
        fs.current_price_ends.set(value=lambda p: p.current_price.ends if p.current_price else None)
        fs.current_price_ends.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))

        fs.last_sold.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        fs.configure(
            include=[
                fs.upc.label("UPC"),
                fs.brand.with_renderer(BrandFieldRenderer),
                fs.description,
                fs.unit_size,
                fs.unit_of_measure.label("Unit of Measure"),
                fs.size,
                fs.weighed,
                fs.case_pack,
                fs.department.with_renderer(forms.DepartmentFieldRenderer),
                fs.subdepartment.with_renderer(forms.SubdepartmentFieldRenderer),
                fs.category.with_renderer(forms.CategoryFieldRenderer),
                fs.family,
                fs.report_code,
                fs.regular_price,
                fs.current_price,
                fs.current_price_ends,
                fs.deposit_link,
                fs.tax,
                fs.organic,
                fs.discountable,
                fs.special_order,
                fs.not_for_sale,
                fs.deleted,
                fs.last_sold,
                ])
        if not self.readonly:
            del fs.regular_price
            del fs.current_price
        if not self.request.has_perm('products.view_deleted'):
            del fs.deleted
        return fs

    def pre_crud(self, product):
        self.product_deleted = not self.creating and product.deleted

    def post_crud(self, product, form):
        if self.product_deleted:
            self.request.session.flash("This product is marked as deleted.", 'error')

    def template_kwargs(self, form):
        kwargs = super(ProductCrud, self).template_kwargs(form)
        kwargs['image'] = False
        product = form.fieldset.model
        if product.upc:
            kwargs['image_url'] = get_image_url(
                self.request.rattail_config, product.upc)
            kwargs['image_path'] = get_image_path(
                self.request.rattail_config, product.upc)
            if os.path.exists(kwargs['image_path']):
                kwargs['image'] = True
        return kwargs


class ProductVersionView(VersionView):
    """
    View which shows version history for a product.
    """
    parent_class = model.Product
    route_model_view = 'product.read'
    child_classes = [
        (model.ProductCode, 'product_uuid'),
        (model.ProductCost, 'product_uuid'),
        (model.ProductPrice, 'product_uuid'),
        ]

    def warn_if_deleted(self):
        """
        Maybe set flash warning if product is marked deleted.
        """
        uuid = self.request.matchdict['uuid']
        product = Session.query(model.Product).get(uuid)
        assert product, "No product found for UUID: {0}".format(repr(uuid))
        if product.deleted:
            self.request.session.flash("This product is marked as deleted.", 'error')

    def list(self):
        self.warn_if_deleted()
        return super(ProductVersionView, self).list()

    def details(self):
        self.warn_if_deleted()
        return super(ProductVersionView, self).details()



def products_search(request):
    """
    Locate a product(s) by UPC.

    Eventually this should be more generic, or at least offer more fields for
    search.  For now it operates only on the ``Product.upc`` field.
    """
    product = None
    upc = request.GET.get('upc', '').strip()
    upc = re.sub(r'\D', '', upc)
    if upc:
        product = get_product_by_upc(Session, upc)
        if not product:
            # Try again, assuming caller did not include check digit.
            upc = GPC(upc, calc_check_digit='upc')
            product = get_product_by_upc(Session, upc)
        if product:
            if product.deleted and not request.has_perm('products.view_deleted'):
                product = None
            else:
                product = {
                    'uuid':                     product.uuid,
                    'upc':                      unicode(product.upc or ''),
                    'full_description':         product.full_description,
                    }
    return {'product': product}


def print_labels(request):
    profile = request.params.get('profile')
    profile = Session.query(LabelProfile).get(profile) if profile else None
    if not profile:
        return {'error': "Label profile not found"}

    product = request.params.get('product')
    product = Session.query(Product).get(product) if product else None
    if not product:
        return {'error': "Product not found"}

    quantity = request.params.get('quantity')
    if not quantity.isdigit():
        return {'error': "Quantity must be numeric"}
    quantity = int(quantity)

    printer = profile.get_printer(request.rattail_config)
    if not printer:
        return {'error': "Couldn't get printer from label profile"}

    try:
        printer.print_labels([(product, quantity)])
    except Exception, error:
        return {'error': str(error)}
    return {}


class CreateProductsBatch(ProductsGrid):

    def make_batch(self, provider, progress):
        from rattail.db import Session
        session = Session()
        configure_session(self.request.rattail_config, session)

        self._filter_config = self.filter_config()
        self._sort_config = self.sort_config()
        products = self.make_query(session)

        batch = provider.make_batch(session, products, progress)
        if not batch:
            session.rollback()
            session.close()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        progress.session.load()
        progress.session['complete'] = True
        progress.session['success_url'] = self.request.route_url('batch.read', uuid=batch.uuid)
        progress.session['success_msg'] = "Batch \"%s\" has been created." % batch.description
        progress.session.save()

    def __call__(self):
        if self.request.POST:
            provider = self.request.POST.get('provider')
            if provider:
                provider = batches.get_provider(self.request.rattail_config, provider)
                if provider:

                    if self.request.POST.get('params') == 'True':
                        provider.set_params(Session(), **self.request.POST)

                    else:
                        try:
                            url = self.request.route_url('batch_params.%s' % provider.name)
                        except KeyError:
                            pass
                        else:
                            self.request.session['referer'] = self.request.current_route_url()
                            return HTTPFound(location=url)
                    
                    progress = SessionProgress(self.request, 'products.batch')
                    thread = Thread(target=self.make_batch, args=(provider, progress))
                    thread.start()
                    kwargs = {
                        'key': 'products.batch',
                        'cancel_url': self.request.route_url('products'),
                        'cancel_msg': "Batch creation was canceled.",
                        }
                    return render_to_response('/progress.mako', kwargs, request=self.request)

        enabled = self.request.rattail_config.get('rattail.pyramid', 'batches.providers')
        if enabled:
            enabled = enabled.split()

        providers = []
        for provider in batches.iter_providers():
            if not enabled or provider.name in enabled:
                providers.append((provider.name, provider.description))

        return {'providers': providers}


def add_routes(config):
    config.add_route('products', '/products')
    config.add_route('products.search', '/products/search')
    config.add_route('products.print_labels', '/products/labels')
    config.add_route('products.create_batch', '/products/batch')
    config.add_route('product.create', '/products/new')
    config.add_route('product.read', '/products/{uuid}')
    config.add_route('product.update', '/products/{uuid}/edit')
    config.add_route('product.delete', '/products/{uuid}/delete')
    

def includeme(config):
    add_routes(config)

    config.add_view(ProductsGrid, route_name='products',
                    renderer='/products/index.mako',
                    permission='products.list')
    config.add_view(print_labels, route_name='products.print_labels',
                    renderer='json', permission='products.print_labels')
    config.add_view(CreateProductsBatch, route_name='products.create_batch',
                    renderer='/products/batch.mako',
                    permission='batches.create')
    config.add_view(ProductCrud, attr='create', route_name='product.create',
                    renderer='/products/crud.mako',
                    permission='products.create')
    config.add_view(ProductCrud, attr='read', route_name='product.read',
                    renderer='/products/read.mako',
                    permission='products.read')
    config.add_view(ProductCrud, attr='update', route_name='product.update',
                    renderer='/products/crud.mako',
                    permission='products.update')
    config.add_view(ProductCrud, attr='delete', route_name='product.delete',
                    permission='products.delete')
    config.add_view(products_search, route_name='products.search',
                    renderer='json', permission='products.list')

    version_defaults(config, ProductVersionView, 'product')
