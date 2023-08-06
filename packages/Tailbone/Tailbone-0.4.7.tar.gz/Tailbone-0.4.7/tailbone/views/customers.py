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
Customer Views
"""

import re

from sqlalchemy import func, and_
from sqlalchemy.orm import joinedload

from tailbone.views import SearchableAlchemyGridView, CrudView, AutocompleteView
from tailbone.forms import EnumFieldRenderer
from tailbone.db import Session

from rattail import enum
from rattail.db import model


class CustomersGrid(SearchableAlchemyGridView):

    mapped_class = model.Customer
    config_prefix = 'customers'
    sort = 'name'

    def join_map(self):
        return {
            'email':
                lambda q: q.outerjoin(model.CustomerEmailAddress, and_(
                    model.CustomerEmailAddress.parent_uuid == model.Customer.uuid,
                    model.CustomerEmailAddress.preference == 1)),
            'phone':
                lambda q: q.outerjoin(model.CustomerPhoneNumber, and_(
                    model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid,
                    model.CustomerPhoneNumber.preference == 1)),
            }

    def filter_map(self):
        return self.make_filter_map(
            exact=['id'],
            name=self.filter_ilike_and_soundex(model.Customer.name),
            email=self.filter_ilike(model.CustomerEmailAddress.address),
            phone=self.filter_ilike(model.CustomerPhoneNumber.number))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_name=True,
            filter_type_name='lk',
            filter_label_phone="Phone Number",
            filter_label_email="Email Address",
            filter_label_id="ID")

    def sort_map(self):
        return self.make_sort_map(
            'id', 'name',
            email=self.sorter(model.CustomerEmailAddress.address),
            phone=self.sorter(model.CustomerPhoneNumber.number))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                ],
            readonly=True)

        if self.request.has_perm('customers.read'):
            g.viewable = True
            g.view_route_name = 'customer.read'
        if self.request.has_perm('customers.update'):
            g.editable = True
            g.edit_route_name = 'customer.update'
        if self.request.has_perm('customers.delete'):
            g.deletable = True
            g.delete_route_name = 'customer.delete'

        return g


class CustomerCrud(CrudView):

    mapped_class = model.Customer
    home_route = 'customers'

    def get_model(self, key):
        customer = super(CustomerCrud, self).get_model(key)
        if customer:
            return customer
        customer = Session.query(model.Customer).filter_by(id=key).first()
        if customer:
            return customer
        person = Session.query(model.CustomerPerson).get(key)
        if person:
            return person.customer
        group = Session.query(model.CustomerGroupAssignment).get(key)
        if group:
            return group.customer
        return None

    def fieldset(self, model):
        fs = self.make_fieldset(model)
        fs.email_preference.set(renderer=EnumFieldRenderer(enum.EMAIL_PREFERENCE))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.email_preference,
                ])
        return fs


class CustomerNameAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer name.
    """
    mapped_class = model.Customer
    fieldname = u'name'


class CustomerPhoneAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer phone number.

    .. note::
       As currently implemented, this view will only work with a PostgreSQL
       database.  It normalizes the user's search term and the database values
       to numeric digits only (i.e. removes special characters from each) in
       order to be able to perform smarter matching.  However normalizing the
       database value currently uses the PG SQL ``regexp_replace()`` function.
    """
    invalid_pattern = re.compile(ur'\D')

    def prepare_term(self, term):
        return self.invalid_pattern.sub(u'', term)

    def query(self, term):
        return Session.query(model.CustomerPhoneNumber)\
            .filter(func.regexp_replace(model.CustomerPhoneNumber.number, ur'\D', u'', u'g').like(u'%{0}%'.format(term)))\
            .order_by(model.CustomerPhoneNumber.number)\
            .options(joinedload(model.CustomerPhoneNumber.customer))

    def display(self, phone):
        return u"{0} {1}".format(phone.number, phone.customer)

    def value(self, phone):
        return phone.customer.uuid


def customer_info(request):
    """
    View which returns simple dictionary of info for a particular customer.
    """
    uuid = request.params.get(u'uuid')
    customer = Session.query(model.Customer).get(uuid) if uuid else None
    if not customer:
        return {}
    return {
        u'uuid':                customer.uuid,
        u'name':                customer.name,
        u'phone_number':        customer.phone.number if customer.phone else u'',
        }


def add_routes(config):
    config.add_route(u'customers',                      u'/customers')
    config.add_route(u'customer.create',                u'/customers/new')
    config.add_route(u'customer.info',                  u'/customers/info')
    config.add_route(u'customers.autocomplete',         u'/customers/autocomplete')
    config.add_route(u'customers.autocomplete.phone',   u'/customers/autocomplete/phone')
    config.add_route(u'customer.read',                  u'/customers/{uuid}')
    config.add_route(u'customer.update',                u'/customers/{uuid}/edit')
    config.add_route(u'customer.delete',                u'/customers/{uuid}/delete')


def includeme(config):
    add_routes(config)

    config.add_view(CustomersGrid, route_name='customers',
                    renderer='/customers/index.mako',
                    permission='customers.list')

    config.add_view(CustomerCrud, attr='create', route_name='customer.create',
                    renderer='/customers/crud.mako',
                    permission='customers.create')
    config.add_view(CustomerCrud, attr='read', route_name='customer.read',
                    renderer='/customers/read.mako',
                    permission='customers.read')
    config.add_view(CustomerCrud, attr='update', route_name='customer.update',
                    renderer='/customers/crud.mako',
                    permission='customers.update')
    config.add_view(CustomerCrud, attr='delete', route_name='customer.delete',
                    permission='customers.delete')

    config.add_view(CustomerNameAutocomplete, route_name=u'customers.autocomplete',
                    renderer=u'json',
                    permission=u'customers.list')
    config.add_view(CustomerPhoneAutocomplete, route_name=u'customers.autocomplete.phone',
                    renderer=u'json',
                    permission=u'customers.list')

    config.add_view(customer_info, route_name=u'customer.info',
                    renderer=u'json',
                    permission=u'customers.read')
