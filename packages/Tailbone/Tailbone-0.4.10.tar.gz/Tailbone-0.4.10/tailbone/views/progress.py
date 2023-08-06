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
Progress Views
"""

from ..progress import get_progress_session


def progress(request):
    key = request.matchdict['key']
    session = get_progress_session(request, key)
    if session.get('complete'):
        msg = session.get('success_msg')
        if msg:
            request.session.flash(msg)
    elif session.get('error'):
        request.session.flash(session.get('error_msg', "An unspecified error occurred."), 'error')
    return session


def cancel(request):
    key = request.matchdict['key']
    session = get_progress_session(request, key)
    session.clear()
    session['canceled'] = True
    session.save()
    msg = request.params.get('cancel_msg', "The operation was canceled.")
    request.session.flash(msg)
    return {}


def includeme(config):
    config.add_route('progress', '/progress/{key}')
    config.add_view(progress, route_name='progress', renderer='json')

    config.add_route('progress.cancel', '/progress/{key}/cancel')
    config.add_view(cancel, route_name='progress.cancel', renderer='json')
