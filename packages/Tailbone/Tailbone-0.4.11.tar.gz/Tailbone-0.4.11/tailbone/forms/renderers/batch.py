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
Batch Field Renderers
"""

from __future__ import unicode_literals

import os
import stat
import random

from formalchemy.ext import fsblob
from formalchemy.fields import FileFieldRenderer as Base
from formalchemy.helpers import hidden_field


class FileFieldRenderer(fsblob.FileFieldRenderer):
    """
    Custom file field renderer for batches based on a single source data file.
    In edit mode, shows a file upload field.  In readonly mode, shows the
    filename and its size.
    """

    @classmethod
    def new(cls, view):
        name = 'Configured%s_%s' % (cls.__name__, str(random.random())[2:])
        return type(str(name), (cls,), dict(view=view))

    @property
    def storage_path(self):
        return self.view.upload_dir

    def get_size(self):
        size = super(FileFieldRenderer, self).get_size()
        if size:
            return size
        batch = self.field.parent.model
        path = os.path.join(self.view.handler.datadir(batch), self.field.value)
        if os.path.isfile(path):
            return os.stat(path)[stat.ST_SIZE]
        return 0

    def get_url(self, filename):
        batch = self.field.parent.model
        return self.view.request.route_url('{0}.download'.format(self.view.route_prefix), uuid=batch.uuid)

    def render(self, **kwargs):
        return Base.render(self, **kwargs)
