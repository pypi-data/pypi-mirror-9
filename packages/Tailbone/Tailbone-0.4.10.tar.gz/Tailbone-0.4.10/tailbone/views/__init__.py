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
Pyramid Views
"""

from tailbone.views.core import View
from tailbone.views.grids import (
    GridView, AlchemyGridView, SortableAlchemyGridView,
    PagedAlchemyGridView, SearchableAlchemyGridView)
from .crud import *
from tailbone.views.autocomplete import AutocompleteView


def home(request):
    """
    Default home view.
    """

    return {}


def add_routes(config):
    config.add_route('home', '/')


def includeme(config):
    add_routes(config)

    config.add_view(home, route_name='home',
                    renderer='/home.mako')

    config.include('tailbone.views.core')

    config.include('tailbone.views.auth')
    config.include('tailbone.views.batches')
    config.include('tailbone.views.brands')
    config.include('tailbone.views.categories')
    config.include('tailbone.views.customergroups')
    config.include('tailbone.views.customers')
    config.include('tailbone.views.departments')
    config.include('tailbone.views.depositlinks')
    config.include('tailbone.views.employees')
    config.include('tailbone.views.families')
    config.include('tailbone.views.labels')
    config.include('tailbone.views.people')
    config.include('tailbone.views.products')
    config.include('tailbone.views.progress')
    config.include(u'tailbone.views.reportcodes')
    config.include('tailbone.views.roles')
    config.include('tailbone.views.stores')
    config.include('tailbone.views.subdepartments')
    config.include('tailbone.views.taxes')
    config.include('tailbone.views.users')
    config.include('tailbone.views.vendors')
