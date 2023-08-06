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
Grid Search Filters
"""

from __future__ import unicode_literals

import re

from sqlalchemy import func, or_

from webhelpers.html import tags
from webhelpers.html import literal

from pyramid.renderers import render
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from edbob.util import prettify

from rattail.core import Object
from rattail.gpc import GPC


class SearchFilter(Object):
    """
    Base class and default implementation for search filters.
    """

    def __init__(self, name, label=None, **kwargs):
        Object.__init__(self, **kwargs)
        self.name = name
        self.label = label or prettify(name)

    def types_select(self):
        types = [
            ('is', "is"),
            ('nt', "is not"),
            ('lk', "contains"),
            ('nl', "doesn't contain"),
            (u'sx', u"sounds like"),
            (u'nx', u"doesn't sound like"),
            ]
        options = []
        filter_map = self.search.filter_map[self.name]
        for value, label in types:
            if value in filter_map:
                options.append((value, label))
        return tags.select('filter_type_'+self.name,
                           self.search.config.get('filter_type_'+self.name),
                           options, class_='filter-type')

    def value_control(self):
        return tags.text(self.name, self.search.config.get(self.name))


class BooleanSearchFilter(SearchFilter):
    """
    Boolean search filter.
    """

    def value_control(self):
        return tags.select(self.name, self.search.config.get(self.name),
                           ["True", "False"])


def EnumSearchFilter(enum):
    options = enum.items()

    class EnumSearchFilter(SearchFilter):
        def value_control(self):
            return tags.select(self.name, self.search.config.get(self.name), options)

    return EnumSearchFilter


class SearchForm(Form):
    """
    Generic form class which aggregates :class:`SearchFilter` instances.
    """

    def __init__(self, request, filter_map, config, *args, **kwargs):
        super(SearchForm, self).__init__(request, *args, **kwargs)
        self.filter_map = filter_map
        self.config = config
        self.filters = {}

    def add_filter(self, filter_):
        filter_.search = self
        self.filters[filter_.name] = filter_


class SearchFormRenderer(FormRenderer):
    """
    Renderer for :class:`SearchForm` instances.
    """

    def __init__(self, form, *args, **kwargs):
        super(SearchFormRenderer, self).__init__(form, *args, **kwargs)
        self.request = form.request
        self.filters = form.filters
        self.config = form.config

    def add_filter(self, visible):
        options = ['add a filter']
        for f in self.sorted_filters():
            options.append((f.name, f.label))
        return self.select('add-filter', options,
                           style='display: none;' if len(visible) == len(self.filters) else None)

    def checkbox(self, name, checked=None, **kwargs):
        if name.startswith('include_filter_'):
            if checked is None:
                checked = self.config[name]
            return tags.checkbox(name, checked=checked, **kwargs)
        if checked is None:
            checked = False
        return super(SearchFormRenderer, self).checkbox(name, checked=checked, **kwargs)

    def render(self, **kwargs):
        kwargs['search'] = self
        return literal(render('/grids/search.mako', kwargs))

    def sorted_filters(self):
        return sorted(self.filters.values(), key=lambda x: x.label)

    def text(self, name, **kwargs):
        return tags.text(name, value=self.config.get(name), **kwargs)


def filter_exact(field):
    """
    Convenience function which returns a filter map entry, with typical logic
    built in for "exact match" queries applied to ``field``.
    """

    return {
        'is':
            lambda q, v: q.filter(field == v) if v else q,
        'nt':
            lambda q, v: q.filter(field != v) if v else q,
        }


def filter_ilike(field):
    """
    Convenience function which returns a filter map entry, with typical logic
    built in for "ILIKE" queries applied to ``field``.
    """

    def ilike(query, value):
        if value:
            query = query.filter(field.ilike('%%%s%%' % value))
        return query

    def not_ilike(query, value):
        if value:
            query = query.filter(or_(
                    field == None,
                    ~field.ilike('%%%s%%' % value),
                    ))
        return query
    
    return {'lk': ilike, 'nl': not_ilike}


def filter_int(field):
    """
    Returns a filter map entry for an integer field.  This provides exact
    matching but also strips out non-numeric characters to avoid type errors.
    """

    def filter_is(q, v):
        v = re.sub(r'\D', '', v or '')
        return q.filter(field == int(v)) if v else q

    def filter_nt(q, v):
        v = re.sub(r'\D', '', v or '')
        return q.filter(field != int(v)) if v else q

    return {'is': filter_is, 'nt': filter_nt}


def filter_soundex(field):
    """
    Returns a filter map entry which leverages the `soundex()` SQL function.
    """

    def soundex(query, value):
        if value:
            query = query.filter(func.soundex(field) == func.soundex(value))
        return query

    def not_soundex(query, value):
        if value:
            query = query.filter(func.soundex(field) != func.soundex(value))
        return query

    return {u'sx': soundex, u'nx': not_soundex}


def filter_ilike_and_soundex(field):
    """
    Returns a filter map which provides both the `ilike` and `soundex`
    features.
    """
    filters = filter_ilike(field)
    filters.update(filter_soundex(field))
    return filters


def filter_gpc(field):
    """
    Returns a filter suitable for a GPC field.
    """

    def filter_is(q, v):
        if not v:
            return q
        try:
            return q.filter(field.in_((
                        GPC(v), GPC(v, calc_check_digit='upc'))))
        except ValueError:
            return q

    def filter_not(q, v):
        if not v:
            return q
        try:
            return q.filter(~field.in_((
                        GPC(v), GPC(v, calc_check_digit='upc'))))
        except ValueError:
            return q

    return {'is': filter_is, 'nt': filter_not}


def get_filter_config(prefix, request, filter_map, **kwargs):
    """
    Returns a configuration dictionary for a search form.
    """

    config = {}

    def update_config(dict_, prefix='', exclude_by_default=False):
        """
        Updates the ``config`` dictionary based on the contents of ``dict_``.
        """

        for field in filter_map:
            if prefix+'include_filter_'+field in dict_:
                include = dict_[prefix+'include_filter_'+field]
                include = bool(include) and include != '0'
                config['include_filter_'+field] = include
            elif exclude_by_default:
                config['include_filter_'+field] = False
            if prefix+'filter_type_'+field in dict_:
                config['filter_type_'+field] = dict_[prefix+'filter_type_'+field]
            if prefix+field in dict_:
                config[field] = dict_[prefix+field]

    # Update config to exclude all filters by default.
    for field in filter_map:
        config['include_filter_'+field] = False

    # Update config to honor default settings.
    config.update(kwargs)

    # Update config with data cached in session.
    update_config(request.session, prefix=prefix+'.')

    # Update config with data from GET/POST request.
    if request.params.get('filters') == 'true':
        update_config(request.params, exclude_by_default=True)

    # Cache filter data in session.
    for key in config:
        if (not key.startswith('filter_factory_')
            and not key.startswith('filter_label_')):
            request.session[prefix+'.'+key] = config[key]

    return config


def get_filter_map(cls, exact=[], ilike=[], int_=[], **kwargs):
    """
    Convenience function which returns a "filter map" for ``cls``.

    ``exact``, if provided, should be a list of field names for which "exact"
    filtering is to be allowed.

    ``ilike``, if provided, should be a list of field names for which "ILIKE"
    filtering is to be allowed.

    ``int_``, if provided, should be a list of field names for which "integer"
    filtering is to be allowed.

    Any remaining ``kwargs`` are assumed to be filter map entries themselves,
    and are added directly to the map.
    """

    fmap = {}
    for name in exact:
        fmap[name] = filter_exact(getattr(cls, name))
    for name in ilike:
        fmap[name] = filter_ilike(getattr(cls, name))
    for name in int_:
        fmap[name] = filter_int(getattr(cls, name))
    fmap.update(kwargs)
    return fmap


def get_search_form(request, filter_map, config):
    """
    Returns a :class:`SearchForm` instance with a :class:`SearchFilter` for
    each filter in ``filter_map``, using configuration from ``config``.
    """

    search = SearchForm(request, filter_map, config)
    for field in filter_map:
        factory = config.get('filter_factory_%s' % field, SearchFilter)
        label = config.get('filter_label_%s' % field)
        search.add_filter(factory(field, label=label))
    return search


def filter_query(query, config, filter_map, join_map):
    """
    Filters the given query according to filter and sorting hints found within
    the config dictionary, using the filter and join maps as needed.  The
    filtered query is returned.
    """
    joins = config.setdefault('joins', [])
    for key in config:
        if key.startswith('include_filter_') and config[key]:
            field = key[15:]
            value = config.get(field)
            if value != '':
                if field in join_map and field not in joins:
                    query = join_map[field](query)
                    joins.append(field)
                fmap = filter_map[field]
                filt = fmap[config['filter_type_'+field]]
                query = filt(query, value)
    return query
