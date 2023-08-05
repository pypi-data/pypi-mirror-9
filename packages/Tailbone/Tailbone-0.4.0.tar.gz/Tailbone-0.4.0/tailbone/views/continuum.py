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
Continuum Version Views
"""

from __future__ import unicode_literals

import sqlalchemy as sa
import sqlalchemy_continuum as continuum

from rattail.db import model
from rattail.db.model.continuum import model_transaction_query

import formalchemy
from pyramid.httpexceptions import HTTPNotFound

from tailbone.db import Session
from tailbone.views import PagedAlchemyGridView, View
from tailbone.forms import DateTimeFieldRenderer


class VersionView(PagedAlchemyGridView):
    """
    View which shows version history for a model instance.
    """

    @property
    def parent_class(self):
        """
        Model class which is "parent" to the version class.
        """
        raise NotImplementedError("Please set `parent_class` on your `VersionView` subclass.")

    @property
    def child_classes(self):
        """
        Model class(es) which are "children" to the version's parent class.
        """
        return []

    @property
    def model_title(self):
        """
        Human-friendly title for the parent model class.
        """
        return self.parent_class.__name__

    @property
    def model_title_plural(self):
        """
        Plural version of the human-friendly title for the parent model class.
        """
        return '{0}s'.format(self.model_title)

    @property
    def prefix(self):
        return self.parent_class.__name__.lower()

    @property
    def config_prefix(self):
        return self.prefix

    @property
    def transaction_class(self):
        return continuum.transaction_class(self.parent_class)

    @property
    def mapped_class(self):
        return self.transaction_class

    @property
    def version_class(self):
        return continuum.version_class(self.parent_class)

    @property
    def route_model_list(self):
        return '{0}s'.format(self.prefix)

    @property
    def route_model_view(self):
        return self.prefix

    def join_map(self):
        return {
            'user':
                lambda q: q.outerjoin(model.User, self.transaction_class.user_uuid == model.User.uuid),
            }

    def sort_config(self):
        return self.make_sort_config(sort='issued_at', dir='desc')

    def sort_map(self):
        return self.make_sort_map('issued_at', 'remote_addr',
            user=self.sorter(model.User.username))

    def transaction_query(self, session=Session):
        uuid = self.request.matchdict['uuid']
        return model_transaction_query(session, uuid, self.parent_class,
                                       child_classes=self.child_classes)

    def make_query(self, session=Session):
        query = self.transaction_query(session)
        return self.modify_query(query)

    def grid(self):
        g = self.make_grid()
        g.issued_at.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        g.configure(
            include=[
                g.issued_at.label("When"),
                g.user.label("Who"),
                g.remote_addr.label("Client IP"),
                ],
            readonly=True)
        g.viewable = True
        g.view_route_name = '{0}.version'.format(self.prefix)
        g.view_route_kwargs = self.view_route_kwargs
        return g

    def render_kwargs(self):
        instance = Session.query(self.parent_class).get(self.request.matchdict['uuid'])
        return {'model_title': self.model_title,
                'model_title_plural': self.model_title_plural,
                'model_instance': instance,
                'route_model_list': self.route_model_list,
                'route_model_view': self.route_model_view}

    def view_route_kwargs(self, transaction):
        return {'uuid': self.request.matchdict['uuid'],
                'transaction_id': transaction.id}

    def list(self):
        """
        View which shows the version history list for a model instance.
        """
        return self()

    def details(self):
        """
        View which shows the change details of a model version.
        """
        kwargs = self.render_kwargs()
        uuid = self.request.matchdict['uuid']
        transaction_id = self.request.matchdict['transaction_id']
        transaction = Session.query(self.transaction_class).get(transaction_id)
        if not transaction:
            raise HTTPNotFound

        version = Session.query(self.version_class).get((uuid, transaction_id))

        def normalize_child_classes():
            classes = []
            for cls in self.child_classes:
                if not isinstance(cls, tuple):
                    cls = (cls, 'uuid')
                classes.append(cls)
            return classes

        versions = []
        if version:
            versions.append(version)
        for model_class, attr in normalize_child_classes():
            if isinstance(model_class, type) and issubclass(model_class, model.Base):
                cls = continuum.version_class(model_class)
                ver = Session.query(cls).filter_by(transaction_id=transaction_id, **{attr: uuid}).first()
                if ver:
                    versions.append(ver)

        previous_transaction = self.transaction_query()\
            .order_by(self.transaction_class.id.desc())\
            .filter(self.transaction_class.id < transaction.id)\
            .first()

        next_transaction = self.transaction_query()\
            .order_by(self.transaction_class.id.asc())\
            .filter(self.transaction_class.id > transaction.id)\
            .first()

        kwargs.update({
                'route_prefix': self.prefix,
                'version': version,
                'transaction': transaction,
                'versions': versions,
                'parent_class': continuum.parent_class,
                'previous_transaction': previous_transaction,
                'next_transaction': next_transaction,
                })

        return kwargs


def version_defaults(config, VersionView, prefix, template_prefix=None):
    """
    Apply default route/view configuration for the given ``VersionView``.
    """
    if template_prefix is None:
        template_prefix = '/{0}s'.format(prefix)
    template_prefix = template_prefix.rstrip('/')

    # list changesets
    config.add_route('{0}.versions'.format(prefix), '/{0}/{{uuid}}/changesets/'.format(prefix))
    config.add_view(VersionView, attr='list', route_name='{0}.versions'.format(prefix),
                    renderer='{0}/versions/index.mako'.format(template_prefix),
                    permission='{0}.versions.view'.format(prefix))

    # view changeset
    config.add_route('{0}.version'.format(prefix), '/{0}/{{uuid}}/changeset/{{transaction_id}}'.format(prefix))
    config.add_view(VersionView, attr='details', route_name='{0}.version'.format(prefix),
                    renderer='{0}/versions/view.mako'.format(template_prefix),
                    permission='{0}.versions.view'.format(prefix))
