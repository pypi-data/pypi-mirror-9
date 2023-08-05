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
CRUD View
"""

from __future__ import unicode_literals

try:
    from sqlalchemy.inspection import inspect
except ImportError:
    inspect = None
    from sqlalchemy.orm import class_mapper

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from .core import View

from ..forms import AlchemyForm
from formalchemy import FieldSet
from ..db import Session

from edbob.util import prettify


__all__ = ['CrudView']


class CrudView(View):

    readonly = False
    allow_successive_creates = False
    update_cancel_route = None

    @property
    def mapped_class(self):
        raise NotImplementedError

    @property
    def pretty_name(self):
        return self.mapped_class.__name__

    @property
    def home_route(self):
        raise NotImplementedError

    @property
    def home_url(self):
        return self.request.route_url(self.home_route)

    @property
    def cancel_route(self):
        return self.home_route

    @property
    def cancel_url(self):
        return self.request.route_url(self.cancel_route)

    def make_fieldset(self, model, **kwargs):
        kwargs.setdefault('session', Session())
        kwargs.setdefault('request', self.request)
        fieldset = FieldSet(model, **kwargs)
        fieldset.prettify = prettify
        return fieldset

    def fieldset(self, model):
        return self.make_fieldset(model)

    def make_form(self, model, form_factory=AlchemyForm, **kwargs):
        if self.readonly:
            self.creating = False
            self.updating = False
        else:
            self.creating = model is self.mapped_class
            self.updating = not self.creating

        fieldset = self.fieldset(model)
        kwargs.setdefault('pretty_name', self.pretty_name)
        kwargs.setdefault('action_url', self.request.current_route_url())
        if self.updating and self.update_cancel_route:
            kwargs.setdefault('cancel_url', self.request.route_url(
                    self.update_cancel_route, uuid=model.uuid))
        else:
            kwargs.setdefault('cancel_url', self.cancel_url)
        kwargs.setdefault('creating', self.creating)
        kwargs.setdefault('updating', self.updating)
        form = form_factory(self.request, fieldset, **kwargs)

        if form.creating:
            if hasattr(self, 'create_label'):
                form.create_label = self.create_label
            if self.allow_successive_creates:
                form.allow_successive_creates = True
                if hasattr(self, 'successive_create_label'):
                    form.successive_create_label = self.successive_create_label

        return form

    def form(self, model):
        return self.make_form(model)

    def crud(self, model, readonly=False):

        if readonly:
            self.readonly = True

        form = self.form(model)
        if readonly:
            form.readonly = True

        if not form.readonly and self.request.POST:
            if form.validate():
                form.save()

                result = self.post_save(form)
                if result:
                    return result

                if form.creating:
                    self.flash_create(form.fieldset.model)
                else:
                    self.flash_update(form.fieldset.model)

                if (form.creating and form.allow_successive_creates
                    and self.request.params.get('create_and_continue')):
                    return HTTPFound(location=self.request.current_route_url())

                return HTTPFound(location=self.post_save_url(form))

            self.validation_failed(form)

        kwargs = self.template_kwargs(form)
        kwargs['form'] = form
        return kwargs

    def template_kwargs(self, form):
        return {}

    def post_save(self, form):
        pass

    def post_save_url(self, form):
        return self.home_url

    def validation_failed(self, form):
        pass

    def flash_create(self, model):
        self.request.session.flash("%s \"%s\" has been created." %
                                   (self.pretty_name, model))

    def flash_delete(self, model):
        self.request.session.flash("%s \"%s\" has been deleted." %
                                   (self.pretty_name, model))
        
    def flash_update(self, model):
        self.request.session.flash("%s \"%s\" has been updated." %
                                   (self.pretty_name, model))

    def create(self):
        return self.crud(self.mapped_class)

    def get_model_from_request(self):
        if inspect:
            mapper = inspect(self.mapped_class)
        else:
            mapper = class_mapper(self.mapped_class)
        assert len(mapper.primary_key) == 1
        key = self.request.matchdict[mapper.primary_key[0].key]
        return self.get_model(key)

    def get_model(self, key):
        model = Session.query(self.mapped_class).get(key)
        return model

    def read(self):
        model = self.get_model_from_request()
        if not model:
            return HTTPNotFound()
        return self.crud(model, readonly=True)

    def update(self):
        model = self.get_model_from_request()
        if not model:
            return HTTPNotFound()
        return self.crud(model)

    def delete(self):
        model = self.get_model_from_request()
        if not model:
            return HTTPNotFound()
        result = self.pre_delete(model)
        if result:
            return result
        Session.delete(model)
        Session.flush() # Don't set flash message if delete fails.
        self.post_delete(model)
        self.flash_delete(model)
        return HTTPFound(location=self.home_url)

    def pre_delete(self, model):
        pass

    def post_delete(self, model):
        pass
