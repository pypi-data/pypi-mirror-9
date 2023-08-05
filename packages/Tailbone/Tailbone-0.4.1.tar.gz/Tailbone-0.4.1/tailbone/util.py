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
Utilities
"""

from __future__ import unicode_literals

import pytz
import humanize

from webhelpers.html import HTML

from rattail.time import timezone


def pretty_datetime(config, value):
    """
    Formats a datetime as a "pretty" human-readable string, with a tooltip
    showing the ISO string value.

    :param config: Reference to a config object.

    :param value: A ``datetime.datetime`` instance.  Note that if this instance
       is not timezone-aware, its timezone is assumed to be UTC.
    """
    if not value:
        return ''

    # Make sure we're dealing with a tz-aware value.  If we're given a naive
    # value, we assume it to be local to the UTC timezone.
    if not value.tzinfo:
        value = pytz.utc.localize(value)

    # Convert value to local timezone, and make a naive copy.
    local = timezone(config)
    value = local.normalize(value.astimezone(local))
    naive_value = value.replace(tzinfo=None)

    return HTML.tag('span',
                    title=value.strftime('%Y-%m-%d %H:%M:%S %Z%z'),
                    c=humanize.naturaltime(naive_value))
