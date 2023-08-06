#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
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
Core View
"""


__all__ = ['View']


class View(object):
    """
    Base for all class-based views.
    """

    def __init__(self, request):
        self.request = request


def fake_error(request):
    """
    View which raises a fake error, to test exception handling.
    """
    raise Exception("Fake error, to test exception handling.")


def includeme(config):
    config.add_route('fake_error', '/fake-error')
    config.add_view(fake_error, route_name='fake_error',
                    permission='admin')
