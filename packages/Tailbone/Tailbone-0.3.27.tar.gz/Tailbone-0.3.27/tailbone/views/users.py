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
User Views
"""

from __future__ import unicode_literals

from formalchemy import Field
from formalchemy.fields import SelectFieldRenderer

from edbob.pyramid.views import users

from . import SearchableAlchemyGridView, CrudView
from ..forms import PersonFieldLinkRenderer
from ..db import Session
from rattail.db.model import User, Person, Role
from rattail.db.auth import guest_role

from webhelpers.html import tags
from webhelpers.html import HTML

from tailbone.grids.search import BooleanSearchFilter


class UsersGrid(SearchableAlchemyGridView):

    mapped_class = User
    config_prefix = 'users'
    sort = 'username'

    def join_map(self):
        return {
            'person':
                lambda q: q.outerjoin(Person),
            }

    def filter_map(self):
        return self.make_filter_map(
            ilike=['username'],
            exact=['active'],
            person=self.filter_ilike(Person.display_name))

    def filter_config(self):
        return self.make_filter_config(
            include_filter_username=True,
            filter_type_username='lk',
            include_filter_person=True,
            filter_type_person='lk',
            filter_factory_active=BooleanSearchFilter,
            include_filter_active=True,
            filter_type_active='is',
            active='True')

    def sort_map(self):
        return self.make_sort_map(
            'username',
            person=self.sorter(Person.display_name))

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.username,
                g.person,
                ],
            readonly=True)
        if self.request.has_perm('users.read'):
            g.viewable = True
            g.view_route_name = 'user.read'
        if self.request.has_perm('users.update'):
            g.editable = True
            g.edit_route_name = 'user.update'
        if self.request.has_perm('users.delete'):
            g.deletable = True
            g.delete_route_name = 'user.delete'
        return g


class RolesField(Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('options', self.get_options())
        kwargs.setdefault('multiple', True)
        super(RolesField, self).__init__(name, **kwargs)

    def get_value(self, user):
        return [x.uuid for x in user.roles]

    def get_options(self):
        return Session.query(Role.name, Role.uuid)\
            .filter(Role.uuid != guest_role(Session()).uuid)\
            .order_by(Role.name)\
            .all()

    def sync(self):
        if not self.is_readonly():
            user = self.model
            roles = Session.query(Role)
            data = self.renderer.deserialize()
            user.roles = [roles.get(x) for x in data]
                

def RolesFieldRenderer(request):

    class RolesFieldRenderer(SelectFieldRenderer):

        def render_readonly(self, **kwargs):
            roles = Session.query(Role)
            html = ''
            for uuid in self.value:
                role = roles.get(uuid)
                link = tags.link_to(
                    role.name, request.route_url('role.read', uuid=role.uuid))
                html += HTML.tag('li', c=link)
            html = HTML.tag('ul', c=html)
            return html

    return RolesFieldRenderer


class UserCrud(CrudView):

    mapped_class = User
    home_route = 'users'

    def fieldset(self, user):
        fs = self.make_fieldset(user)

        # Must set Person options to empty set to avoid unwanted magic.
        fs.person.set(options=[])

        fs.append(users.PasswordField('password'))
        fs.append(Field('confirm_password',
                        renderer=users.PasswordFieldRenderer))
        fs.append(RolesField(
                'roles', renderer=RolesFieldRenderer(self.request)))

        fs.configure(
            include=[
                fs.username,
                fs.person.with_renderer(PersonFieldLinkRenderer),
                fs.password.label("Set Password"),
                fs.confirm_password,
                fs.roles,
                fs.active,
                ])

        if self.readonly:
            del fs.password
            del fs.confirm_password

        return fs


def add_routes(config):
    config.add_route(u'users',          u'/users')
    config.add_route(u'user.create',    u'/users/new')
    config.add_route(u'user.read',      u'/users/{uuid}')
    config.add_route(u'user.update',    u'/users/{uuid}/edit')
    config.add_route(u'user.delete',    u'/users/{uuid}/delete')


def includeme(config):
    add_routes(config)

    # List
    config.add_view(UsersGrid, route_name='users',
                    renderer='/users/index.mako',
                    permission='users.list')

    # CRUD
    config.add_view(UserCrud, attr='create', route_name='user.create',
                    renderer='/users/crud.mako',
                    permission='users.create')
    config.add_view(UserCrud, attr='read', route_name='user.read',
                    renderer='/users/crud.mako',
                    permission='users.read')
    config.add_view(UserCrud, attr='update', route_name='user.update',
                    renderer='/users/crud.mako',
                    permission='users.update')
    config.add_view(UserCrud, attr='delete', route_name='user.delete',
                    permission='users.delete')
