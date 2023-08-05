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
Print Labels Batch
"""

from __future__ import unicode_literals

from rattail.db import model

from tailbone.db import Session
from tailbone.views.batches.params import BatchParamsView


class PrintLabels(BatchParamsView):

    provider_name = 'print_labels'

    def render_kwargs(self):
        q = Session.query(model.LabelProfile)
        q = q.order_by(model.LabelProfile.ordinal)
        profiles = [(x.code, x.description) for x in q]
        return {'label_profiles': profiles}


def includeme(config):
    
    config.add_route('batch_params.print_labels', '/batches/params/print-labels')
    config.add_view(PrintLabels, route_name='batch_params.print_labels',
                    renderer='/batches/params/print_labels.mako',
                    permission='batches.print_labels')
