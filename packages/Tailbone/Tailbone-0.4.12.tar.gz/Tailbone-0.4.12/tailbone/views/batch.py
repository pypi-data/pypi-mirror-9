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
Base views for maintaining new-style batches.

.. note::
   This is all still very experimental.
"""

from __future__ import unicode_literals

import os
import datetime
import logging

import formalchemy
from pyramid.renderers import render_to_response
from pyramid.response import FileResponse
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from webhelpers.html.tags import link_to, HTML

from rattail.db import model
from rattail.db import Session as RatSession
from rattail.threads import Thread

from tailbone.db import Session
from tailbone.views import SearchableAlchemyGridView, CrudView
from tailbone.forms import DateTimeFieldRenderer, UserFieldRenderer, EnumFieldRenderer
from tailbone.forms.renderers.batch import FileFieldRenderer
from tailbone.grids.search import BooleanSearchFilter, EnumSearchFilter
from tailbone.progress import SessionProgress


log = logging.getLogger(__name__)


class BaseGrid(SearchableAlchemyGridView):
    """
    Base view for batch and batch row grid views.  You should not derive from
    this class, but :class:`BatchGrid` or :class:`BatchRowGrid` instead.
    """

    @property
    def config_prefix(self):
        """
        Config prefix for the grid view.  This is used to keep track of current
        filtering and sorting, within the user's session.  Derived classes may
        override this.
        """
        return self.mapped_class.__name__.lower()

    @property
    def permission_prefix(self):
        """
        Permission prefix for the grid view.  This is used to automatically
        protect certain views common to all batches.  Derived classes can
        override this.
        """
        return self.route_prefix

    def join_map_extras(self):
        """
        Derived classes can override this.  The value returned will be used to
        supplement the default join map.
        """
        return {}

    def filter_map_extras(self):
        """
        Derived classes can override this.  The value returned will be used to
        supplement the default filter map.
        """
        return {}

    def make_filter_map(self, **kwargs):
        """
        Make a filter map by combining kwargs from the base class, with extras
        supplied by a derived class.
        """
        extras = self.filter_map_extras()
        exact = extras.pop('exact', None)
        if exact:
            kwargs.setdefault('exact', []).extend(exact)
        ilike = extras.pop('ilike', None)
        if ilike:
            kwargs.setdefault('ilike', []).extend(ilike)
        kwargs.update(extras)
        return super(BaseGrid, self).make_filter_map(**kwargs)

    def filter_config_extras(self):
        """
        Derived classes can override this.  The value returned will be used to
        supplement the default filter config.
        """
        return {}

    def sort_map_extras(self):
        """
        Derived classes can override this.  The value returned will be used to
        supplement the default sort map.
        """
        return {}

    def _configure_grid(self, grid):
        """
        Internal method for configuring the grid.  This is meant only for base
        classes; derived classes should not need to override it.
        """

    def configure_grid(self, grid):
        """
        Derived classes can override this.  Customizes a grid which has already
        been created with defaults by the base class.
        """


class BatchGrid(BaseGrid):
    """
    Base grid view for batches, which can be filtered and sorted.
    """

    @property
    def batch_class(self):
        raise NotImplementedError

    @property
    def mapped_class(self):
        return self.batch_class

    @property
    def batch_display(self):
        """
        Singular display text for the batch type, e.g. "Vendor Invoice".
        Override this as necessary.
        """
        return self.batch_class.__name__

    @property
    def batch_display_plural(self):
        """
        Plural display text for the batch type, e.g. "Vendor Invoices".
        Override this as necessary.
        """
        return "{0}s".format(self.batch_display)

    def join_map(self):
        """
        Provides the default join map for batch grid views.  Derived classes
        should *not* override this, but :meth:`join_map_extras()` instead.
        """
        map_ = {
            'created_by':
                lambda q: q.join(model.User, model.User.uuid == self.batch_class.created_by_uuid),
            'executed_by':
                lambda q: q.outerjoin(model.User, model.User.uuid == self.batch_class.executed_by_uuid),
            }
        map_.update(self.join_map_extras())
        return map_

    def filter_map(self):
        """
        Provides the default filter map for batch grid views.  Derived classes
        should *not* override this, but :meth:`filter_map_extras()` instead.
        """

        def executed_is(q, v):
            if v == 'True':
                return q.filter(self.batch_class.executed != None)
            else:
                return q.filter(self.batch_class.executed == None)

        def executed_nt(q, v):
            if v == 'True':
                return q.filter(self.batch_class.executed == None)
            else:
                return q.filter(self.batch_class.executed != None)

        return self.make_filter_map(
            executed={'is': executed_is, 'nt': executed_nt})

    def filter_config(self):
        """
        Provides the default filter config for batch grid views.  Derived
        classes should *not* override this, but :meth:`filter_config_extras()`
        instead.
        """
        config = self.make_filter_config(
            filter_factory_executed=BooleanSearchFilter,
            filter_type_executed='is',
            executed=False,
            include_filter_executed=True)
        config.update(self.filter_config_extras())
        return config

    def sort_map(self):
        """
        Provides the default sort map for batch grid views.  Derived classes
        should *not* override this, but :meth:`sort_map_extras()` instead.
        """
        map_ = self.make_sort_map(
            created_by=self.sorter(model.User.username),
            executed_by=self.sorter(model.User.username))
        map_.update(self.sort_map_extras())
        return map_

    def sort_config(self):
        """
        Provides the default sort config for batch grid views.  Derived classes
        may override this.
        """
        return self.make_sort_config(sort='created', dir='desc')

    def grid(self):
        """
        Creates the grid for the view.  Derived classes should *not* override
        this, but :meth:`configure_grid()` instead.
        """
        g = self.make_grid()
        g.created.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        g.created_by.set(renderer=UserFieldRenderer)
        g.cognized.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        g.cognized_by.set(renderer=UserFieldRenderer)
        g.executed.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        g.executed_by.set(renderer=UserFieldRenderer)
        self._configure_grid(g)
        self.configure_grid(g)
        if self.request.has_perm('{0}.view'.format(self.permission_prefix)):
            g.viewable = True
            g.view_route_name = '{0}.view'.format(self.route_prefix)
        if self.request.has_perm('{0}.edit'.format(self.permission_prefix)):
            g.editable = True
            g.edit_route_name = '{0}.edit'.format(self.route_prefix)
        if self.request.has_perm('{0}.delete'.format(self.permission_prefix)):
            g.deletable = True
            g.delete_route_name = '{0}.delete'.format(self.route_prefix)
        return g

    def _configure_grid(self, grid):
        grid.created_by.set(label="Created by")
        grid.executed_by.set(label="Executed by")

    def configure_grid(self, grid):
        """
        Derived classes can override this.  Customizes a grid which has already
        been created with defaults by the base class.
        """
        g = grid
        g.configure(
            include=[
                g.created,
                g.created_by,
                g.executed,
                g.executed_by,
                ],
            readonly=True)

    def render_kwargs(self):
        """
        Add some things to the template context: batch type display name, route
        and permission prefixes.
        """
        return {
            'batch_display': self.batch_display,
            'batch_display_plural': self.batch_display_plural,
            'route_prefix': self.route_prefix,
            'permission_prefix': self.permission_prefix,
            }


class FileBatchGrid(BatchGrid):
    """
    Base grid view for batches, which involve primarily a file upload.
    """

    def _configure_grid(self, g):
        super(FileBatchGrid, self)._configure_grid(g)
        g.created.set(label="Uploaded")
        g.created_by.set(label="Uploaded by")

    def configure_grid(self, grid):
        """
        Derived classes can override this.  Customizes a grid which has already
        been created with defaults by the base class.
        """
        g = grid
        g.configure(
            include=[
                g.created,
                g.created_by,
                g.filename,
                g.executed,
                g.executed_by,
                ],
            readonly=True)


class BaseCrud(CrudView):
    """
    Base CRUD view for batches and batch rows.
    """
    flash = {}

    @property
    def home_route(self):
        """
        The "home" route for the batch type, i.e. its grid view.
        """
        return self.route_prefix

    @property
    def permission_prefix(self):
        """
        Permission prefix used to generically protect certain views common to
        all batches.  Derived classes can override this.
        """
        return self.route_prefix

    def flash_create(self, model):
        if 'create' in self.flash:
            self.request.session.flash(self.flash['create'])
        else:
            super(BaseCrud, self).flash_create(model)

    def flash_update(self, model):
        if 'update' in self.flash:
            self.request.session.flash(self.flash['update'])
        else:
            super(BaseCrud, self).flash_update(model)

    def flash_delete(self, model):
        if 'delete' in self.flash:
            self.request.session.flash(self.flash['delete'])
        else:
            super(BaseCrud, self).flash_delete(model)


class BatchCrud(BaseCrud):
    """
    Base CRUD view for batches.
    """
    refreshable = False
    flash = {}

    @property
    def batch_class(self):
        raise NotImplementedError

    @property
    def mapped_class(self):
        return self.batch_class

    @property
    def permission_prefix(self):
        """
        Permission prefix for the grid view.  This is used to automatically
        protect certain views common to all batches.  Derived classes can - and
        typically should - override this.
        """
        return self.route_prefix

    @property
    def batch_display_plural(self):
        """
        Plural display text for the batch type.
        """
        return "{0}s".format(self.batch_display)

    def __init__(self, request):
        self.request = request
        self.handler = self.get_handler()

    def get_handler(self):
        """
        Returns a `BatchHandler` instance for the view.  Derived classes may
        override this as needed.  The default is to create an instance of
        :attr:`batch_handler_class`.
        """
        return self.batch_handler_class(self.request.rattail_config)

    def fieldset(self, model):
        """
        Creates the fieldset for the view.  Derived classes should *not*
        override this, but :meth:`configure_fieldset()` instead.
        """
        fs = self.make_fieldset(model)
        fs.created.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        fs.created_by.set(label="Created by", renderer=UserFieldRenderer)
        fs.cognized.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        fs.cognized_by.set(label="Cognized by", renderer=UserFieldRenderer)
        fs.executed.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        fs.executed_by.set(label="Executed by", renderer=UserFieldRenderer)
        self.configure_fieldset(fs)
        if self.creating:
            del fs.created
            del fs.created_by
            del fs.cognized
            del fs.cognized_by
        return fs

    def configure_fieldset(self, fieldset):
        """
        Derived classes can override this.  Customizes a fieldset which has
        already been created with defaults by the base class.
        """
        fs = fieldset
        fs.configure(
            include=[
                fs.created,
                fs.created_by,
                # fs.cognized,
                # fs.cognized_by,
                fs.executed,
                fs.executed_by,
                ])

    def update(self):
        """
        Don't allow editing a batch which has already been executed.
        """
        batch = self.get_model_from_request()
        if not batch:
            return HTTPNotFound()
        if batch.executed:
            return HTTPFound(location=self.view_url(batch.uuid))
        return self.crud(batch)

    def post_create_url(self, form):
        """
        Redirect to view batch after creating a batch.
        """
        batch = form.fieldset.model
        Session.flush()
        return self.view_url(batch.uuid)

    def post_update_url(self, form):
        """
        Redirect back to edit batch page after editing a batch, unless the
        refresh flag is set, in which case do that.
        """
        if self.request.params.get('refresh') == 'true':
            return self.refresh_url()
        return self.request.current_route_url()

    def template_kwargs(self, form):
        """
        Add some things to the template context: current batch model, batch
        type display name, route and permission prefixes, batch row grid.
        """
        batch = form.fieldset.model
        batch.refreshable = self.refreshable
        return {
            'batch': batch,
            'batch_display': self.batch_display,
            'batch_display_plural': self.batch_display_plural,
            'execute_title': self.handler.get_execute_title(batch),
            'route_prefix': self.route_prefix,
            'permission_prefix': self.permission_prefix,
            }

    def flash_create(self, batch):
        if 'create' in self.flash:
            self.request.session.flash(self.flash['create'])
        else:
            super(BatchCrud, self).flash_create(batch)

    def flash_delete(self, batch):
        if 'delete' in self.flash:
            self.request.session.flash(self.flash['delete'])
        else:
            super(BatchCrud, self).flash_delete(batch)

    def current_batch(self):
        """
        Return the current batch, based on the UUID within the URL.
        """
        return Session.query(self.mapped_class).get(self.request.matchdict['uuid'])

    def refresh(self):
        """
        View which will attempt to refresh all data for the batch.  What
        exactly this means will depend on the type of batch etc.
        """
        batch = self.current_batch()

        # If handler doesn't declare the need for progress indicator, things
        # are nice and simple.
        if not self.handler.show_progress:
            self.refresh_data(Session, batch)
            self.request.session.flash("Batch data has been refreshed.")
            return HTTPFound(location=self.view_url(batch.uuid))

        # Showing progress requires a separate thread; start that first.
        key = '{0}.refresh'.format(self.batch_class.__tablename__)
        progress = SessionProgress(self.request, key)
        thread = Thread(target=self.refresh_thread, args=(batch.uuid, progress))
        thread.start()

        # Send user to progress page.
        kwargs = {
            'key': key,
            'cancel_url': self.view_url(batch.uuid),
            'cancel_msg': "Batch refresh was canceled.",
            }
        return render_to_response('/progress.mako', kwargs, request=self.request)

    def refresh_data(self, session, batch, progress=None):
        """
        Instruct the batch handler to refresh all data for the batch.
        """
        self.handler.refresh_data(session, batch, progress=progress)
        batch.cognized = datetime.datetime.utcnow()
        batch.cognized_by = self.request.user

    def refresh_thread(self, batch_uuid, progress):
        """
        Thread target for refreshing batch data with progress indicator.
        """
        # Refresh data for the batch, with progress.  Note that we must use the
        # rattail session here; can't use tailbone because it has web request
        # transaction binding etc.
        session = RatSession()
        batch = session.query(self.batch_class).get(batch_uuid)
        try:
            self.refresh_data(session, batch, progress=progress)
        except Exception as error:
            session.rollback()
            log.exception("refreshing data for batch failed: {0}".format(batch))
            session.close()
            progress.session.load()
            progress.session['error'] = True
            progress.session['error_msg'] = "Data refresh failed: {0}".format(error)
            progress.session.save()
            return

        session.commit()
        session.refresh(batch)
        session.close()

        # Finalize progress indicator.
        progress.session.load()
        progress.session['complete'] = True
        progress.session['success_url'] = self.view_url(batch.uuid)
        progress.session.save()
        
    def view_url(self, uuid=None):
        """
        Returns the URL for viewing a batch; defaults to current batch.
        """
        if uuid is None:
            uuid = self.request.matchdict['uuid']
        return self.request.route_url('{0}.view'.format(self.route_prefix), uuid=uuid)

    def refresh_url(self, uuid=None):
        """
        Returns the URL for refreshing a batch; defaults to current batch.
        """
        if uuid is None:
            uuid = self.request.matchdict['uuid']
        return self.request.route_url('{0}.refresh'.format(self.route_prefix), uuid=uuid)

    def execute(self):
        batch = self.current_batch()
        if self.handler.execute(batch):
            batch.executed = datetime.datetime.utcnow()
            batch.executed_by = self.request.user
        return HTTPFound(location=self.view_url(batch.uuid))


class FileBatchCrud(BatchCrud):
    """
    Base CRUD view for batches which involve a file upload as the first step.
    """
    refreshable = True

    def post_create_url(self, form):
        """
        Redirect to refresh batch after creating a batch.
        """
        batch = form.fieldset.model
        Session.flush()
        return self.refresh_url(batch.uuid)

    @property
    def upload_dir(self):
        """
        The path to the root upload folder, to be used as the ``storage_path``
        argument for the file field renderer.
        """
        uploads = os.path.join(
            self.request.rattail_config.require('rattail', 'batch.files'),
            'uploads')
        uploads = self.request.rattail_config.get(
            'tailbone', 'batch.uploads', default=uploads)
        if not os.path.exists(uploads):
            os.makedirs(uploads)
        return uploads

    def fieldset(self, model):
        """
        Creates the fieldset for the view.  Derived classes should *not*
        override this, but :meth:`configure_fieldset()` instead.
        """
        fs = self.make_fieldset(model)
        fs.created.set(label="Uploaded", renderer=DateTimeFieldRenderer(self.request.rattail_config), readonly=True)
        fs.created_by.set(label="Uploaded by", renderer=UserFieldRenderer, readonly=True)
        fs.cognized.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        fs.cognized_by.set(label="Cognized by", renderer=UserFieldRenderer)
        fs.executed.set(renderer=DateTimeFieldRenderer(self.request.rattail_config))
        fs.executed_by.set(label="Executed by", renderer=UserFieldRenderer)
        fs.filename.set(renderer=FileFieldRenderer.new(self), label="Data File")
        self.configure_fieldset(fs)
        if self.creating:
            del fs.created
            del fs.created_by
            if 'cognized' in fs.render_fields:
                del fs.cognized
            if 'cognized_by' in fs.render_fields:
                del fs.cognized_by
            if 'executed' in fs.render_fields:
                del fs.executed
            if 'executed_by' in fs.render_fields:
                del fs.executed_by
            if 'data_rows' in fs.render_fields:
                del fs.data_rows
        else:
            if self.updating and 'filename' in fs.render_fields:
                fs.filename.set(readonly=True)
            batch = fs.model
            if not batch.executed:
                if 'executed' in fs.render_fields:
                    del fs.executed
                if 'executed_by' in fs.render_fields:
                    del fs.executed_by
        return fs

    def configure_fieldset(self, fieldset):
        """
        Derived classes can override this.  Customizes a fieldset which has
        already been created with defaults by the base class.
        """
        fs = fieldset
        fs.configure(
            include=[
                fs.created,
                fs.created_by,
                fs.filename,
                # fs.cognized,
                # fs.cognized_by,
                fs.executed,
                fs.executed_by,
                ])

    def save_form(self, form):
        """
        Save the uploaded data file if necessary, etc.  If batch initialization
        fails, don't persist the batch at all; the user will be sent back to
        the "create batch" page in that case.
        """
        # Transfer form data to batch instance.
        form.fieldset.sync()
        batch = form.fieldset.model

        # For new batches, assign current user as creator, save file etc.
        if self.creating:
            batch.created_by = self.request.user

            # Expunge batch from session to prevent it from being flushed
            # during init.  This is done as a convenience to views which
            # provide an init method.  Some batches may have required fields
            # which aren't filled in yet, but the view may need to query the
            # database to obtain the values.  This will cause a session flush,
            # and the missing fields will trigger data integrity errors.
            Session.expunge(batch)
            self.batch_inited = self.init_batch(batch)
            if self.batch_inited:
                Session.add(batch)
                Session.flush()

                # Handler saves a copy of the file and updates the batch filename.
                path = os.path.join(self.upload_dir, batch.filename)
                self.handler.set_data_file(batch, path)
                os.remove(path)

    def init_batch(self, batch):
        """
        Initialize a new batch.  Derived classes can override this to
        effectively provide default values for a batch, etc.  This method is
        invoked after a batch has been fully prepared for insertion to the
        database, but before the push to the database occurs.

        Note that the return value of this function matters; if it is boolean
        false then the batch will not be persisted at all, and the user will be
        redirected to the "create batch" page.
        """
        return True

    def post_save(self, form):
        """
        This checks for failed batch initialization when creating a new batch.
        If a failure is detected, the user is redirected to the page for
        creating new batches.  The assumption here is that the
        :meth:`init_batch()` method responsible for indicating the failure will
        have set a flash message for the user with more info.
        """
        if self.creating and not self.batch_inited:
            return HTTPFound(location=self.request.route_url(
                    '{0}.create'.format(self.route_prefix)))

    def pre_delete(self, batch):
        """
        Delete all data (files etc.) for the batch.
        """
        batch.delete_data(self.request.rattail_config)
        del batch.data_rows[:]

    def download(self):
        """
        View for downloading the data file associated with a batch.
        """
        batch = self.current_batch()
        if not batch:
            return HTTPNotFound()
        path = self.handler.data_path(batch)
        response = FileResponse(path, request=self.request)
        response.headers[b'Content-Length'] = str(os.path.getsize(path))
        filename = os.path.basename(batch.filename).encode('ascii', 'replace')
        response.headers[b'Content-Disposition'] = b'attachment; filename="{0}"'.format(filename)
        return response


class StatusRenderer(EnumFieldRenderer):
    """
    Custom renderer for ``status_code`` fields.  Adds ``status_text`` value as
    title attribute if it exists.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        status_code_text = self.enumeration.get(value, unicode(value))
        row = self.field.parent.model
        if row.status_text:
            return HTML.tag('span', title=row.status_text, c=status_code_text)
        return status_code_text


class BatchRowGrid(BaseGrid):
    """
    Base grid view for batch rows, which can be filtered and sorted.  Also it
    can delete all rows matching the current list view query.
    """

    @property
    def row_class(self):
        raise NotImplementedError

    @property
    def mapped_class(self):
        return self.row_class

    @property
    def config_prefix(self):
        """
        Config prefix for the grid view.  This is used to keep track of current
        filtering and sorting, within the user's session.  Derived classes may
        override this.
        """
        return '{0}.{1}'.format(self.mapped_class.__name__.lower(),
                                self.request.matchdict['uuid'])

    @property
    def batch_class(self):
        """
        Model class of the batch to which the rows belong.
        """
        return self.row_class.__batch_class__

    @property
    def batch_display(self):
        """
        Singular display text for the batch type, e.g. "Vendor Invoice".
        Override this as necessary.
        """
        return self.batch_class.__name__

    def current_batch(self):
        """
        Return the current batch, based on the UUID within the URL.
        """
        return Session.query(self.batch_class).get(self.request.matchdict['uuid'])

    def modify_query(self, q):
        q = super(BatchRowGrid, self).modify_query(q)
        q = q.filter_by(batch=self.current_batch())
        q = q.filter_by(removed=False)
        return q

    def join_map(self):
        """
        Provides the default join map for batch row grid views.  Derived
        classes should *not* override this, but :meth:`join_map_extras()`
        instead.
        """
        return self.join_map_extras()

    def filter_map(self):
        """
        Provides the default filter map for batch row grid views.  Derived
        classes should *not* override this, but :meth:`filter_map_extras()`
        instead.
        """
        return self.make_filter_map(exact=['status_code'])

    def filter_config(self):
        """
        Provides the default filter config for batch grid views.  Derived
        classes should *not* override this, but :meth:`filter_config_extras()`
        instead.
        """
        kwargs = {'filter_label_status_code': "Status",
                  'filter_factory_status_code': EnumSearchFilter(self.row_class.STATUS)}
        kwargs.update(self.filter_config_extras())
        return self.make_filter_config(**kwargs)

    def sort_map(self):
        """
        Provides the default sort map for batch grid views.  Derived classes
        should *not* override this, but :meth:`sort_map_extras()` instead.
        """
        map_ = self.make_sort_map()
        map_.update(self.sort_map_extras())
        return map_

    def sort_config(self):
        """
        Provides the default sort config for batch grid views.  Derived classes
        may override this.
        """
        return self.make_sort_config(sort='sequence', dir='asc')

    def grid(self):
        """
        Creates the grid for the view.  Derived classes should *not* override
        this, but :meth:`configure_grid()` instead.
        """
        g = self.make_grid()
        g.extra_row_class = self.tr_class
        g.sequence.set(label="Seq.")
        g.status_code.set(label="Status", renderer=StatusRenderer(self.row_class.STATUS))
        self._configure_grid(g)
        self.configure_grid(g)

        batch = self.current_batch()
        g.viewable = True
        g.view_route_name = '{0}.row.view'.format(self.route_prefix)
        # TODO: Fix this check for edit mode.
        edit_mode = self.request.referrer.endswith('/edit')
        if edit_mode and not batch.executed and self.request.has_perm('{0}.edit'.format(self.permission_prefix)):
            # g.editable = True
            # g.edit_route_name = '{0}.rows.edit'.format(self.route_prefix)
            g.deletable = True
            g.delete_route_name = '{0}.rows.delete'.format(self.route_prefix)
        return g

    def tr_class(self, row, i):
        pass

    def render_kwargs(self):
        """
        Add the current batch and route prefix to the template context.
        """
        return {'batch': self.current_batch(),
                'route_prefix': self.route_prefix}

    def bulk_delete(self):
        """
        "Delete" all rows matching the current row grid view query.  This sets
        the ``removed`` flag on the rows but does not truly delete them.
        """
        self.query().update({'removed': True}, synchronize_session=False)
        return HTTPFound(location=self.request.route_url(
                '{0}.view'.format(self.route_prefix),
                uuid=self.request.matchdict['uuid']))


class ProductBatchRowGrid(BatchRowGrid):
    """
    Base grid view for batch rows which deal directly with products.
    """

    def filter_map(self):
        """
        Provides the default filter map for batch row grid views.  Derived
        classes should *not* override this, but :meth:`filter_map_extras()`
        instead.
        """
        return self.make_filter_map(exact=['status_code'],
                                    ilike=['brand_name', 'description', 'size'],
                                    upc=self.filter_gpc(self.row_class.upc))

    def filter_config(self):
        """
        Provides the default filter config for batch grid views.  Derived
        classes should *not* override this, but :meth:`filter_config_extras()`
        instead.
        """
        kwargs = {'filter_label_status_code': "Status",
                  'filter_factory_status_code': EnumSearchFilter(self.row_class.STATUS),
                  'filter_label_upc': "UPC",
                  'filter_label_brand_name': "Brand"}
        kwargs.update(self.filter_config_extras())
        return self.make_filter_config(**kwargs)


class BatchRowCrud(BaseCrud):
    """
    Base CRUD view for batch rows.
    """

    @property
    def row_class(self):
        raise NotImplementedError

    @property
    def mapped_class(self):
        return self.row_class

    @property
    def batch_class(self):
        """
        Model class of the batch to which the rows belong.
        """
        return self.row_class.__batch_class__

    @property
    def batch_display(self):
        """
        Singular display text for the batch type, e.g. "Vendor Invoice".
        Override this as necessary.
        """
        return self.batch_class.__name__

    def template_kwargs(self, form):
        """
        Add batch row instance etc. to template context.
        """
        row = form.fieldset.model
        return {
            'row': row,
            'batch_display': self.batch_display,
            'route_prefix': self.route_prefix,
            'permission_prefix': self.permission_prefix,
            }

    def delete(self):
        """
        "Delete" a row from the batch.  This sets the ``removed`` flag on the
        row but does not truly delete it.
        """
        row = self.get_model_from_request()
        if not row:
            return HTTPNotFound()
        row.removed = True
        return HTTPFound(location=self.request.route_url(
                '{0}.view'.format(self.route_prefix), uuid=row.batch_uuid))


def defaults(config, batch_grid, batch_crud, row_grid, row_crud, url_prefix,
             route_prefix=None, permission_prefix=None, template_prefix=None):
    """
    Apply default configuration to the Pyramid configurator object, for the
    given batch grid and CRUD views.
    """
    assert batch_grid
    assert batch_crud
    assert url_prefix
    if route_prefix is None:
        route_prefix = batch_grid.route_prefix
    if permission_prefix is None:
        permission_prefix = route_prefix
    if template_prefix is None:
        template_prefix = url_prefix
    template_prefix.rstrip('/')

    # Batches grid
    config.add_route(route_prefix, url_prefix)
    config.add_view(batch_grid, route_name=route_prefix,
                    renderer='{0}/index.mako'.format(template_prefix),
                    permission='{0}.view'.format(permission_prefix))

    # Create batch
    config.add_route('{0}.create'.format(route_prefix), '{0}new'.format(url_prefix))
    config.add_view(batch_crud, attr='create', route_name='{0}.create'.format(route_prefix),
                    renderer='{0}/create.mako'.format(template_prefix),
                    permission='{0}.create'.format(permission_prefix))

    # View batch
    config.add_route('{0}.view'.format(route_prefix), '{0}{{uuid}}'.format(url_prefix))
    config.add_view(batch_crud, attr='read', route_name='{0}.view'.format(route_prefix),
                    renderer='{0}/view.mako'.format(template_prefix),
                    permission='{0}.view'.format(permission_prefix))

    # Edit batch
    config.add_route('{0}.edit'.format(route_prefix), '{0}{{uuid}}/edit'.format(url_prefix))
    config.add_view(batch_crud, attr='update', route_name='{0}.edit'.format(route_prefix),
                    renderer='{0}/edit.mako'.format(template_prefix),
                    permission='{0}.edit'.format(permission_prefix))

    # Refresh batch row data
    config.add_route('{0}.refresh'.format(route_prefix), '{0}{{uuid}}/refresh'.format(url_prefix))
    config.add_view(batch_crud, attr='refresh', route_name='{0}.refresh'.format(route_prefix),
                    permission='{0}.edit'.format(permission_prefix))

    # Execute batch
    config.add_route('{0}.execute'.format(route_prefix), '{0}{{uuid}}/execute'.format(url_prefix))
    config.add_view(batch_crud, attr='execute', route_name='{0}.execute'.format(route_prefix),
                    permission='{0}.execute'.format(permission_prefix))

    # Download batch data file
    if hasattr(batch_crud, 'download'):
        config.add_route('{0}.download'.format(route_prefix), '{0}{{uuid}}/download'.format(url_prefix))
        config.add_view(batch_crud, attr='download', route_name='{0}.download'.format(route_prefix),
                        permission='{0}.download'.format(permission_prefix))

    # Delete batch
    config.add_route('{0}.delete'.format(route_prefix), '{0}{{uuid}}/delete'.format(url_prefix))
    config.add_view(batch_crud, attr='delete', route_name='{0}.delete'.format(route_prefix),
                    permission='{0}.delete'.format(permission_prefix))

    # Batch rows grid
    config.add_route('{0}.rows'.format(route_prefix), '{0}{{uuid}}/rows/'.format(url_prefix))
    config.add_view(row_grid, route_name='{0}.rows'.format(route_prefix),
                    renderer='/batch/rows.mako',
                    permission='{0}.view'.format(permission_prefix))

    # view batch row
    config.add_route('{0}.row.view'.format(route_prefix), '{0}row/{{uuid}}'.format(url_prefix))
    config.add_view(row_crud, attr='read', route_name='{0}.row.view'.format(route_prefix),
                    renderer='{0}/row.view.mako'.format(template_prefix),
                    permission='{0}.view'.format(permission_prefix))

    # Bulk delete batch rows
    config.add_route('{0}.rows.bulk_delete'.format(route_prefix), '{0}{{uuid}}/rows/delete'.format(url_prefix))
    config.add_view(row_grid, attr='bulk_delete', route_name='{0}.rows.bulk_delete'.format(route_prefix),
                    permission='{0}.edit'.format(permission_prefix))

    # Delete batch row
    config.add_route('{0}.rows.delete'.format(route_prefix), '{0}delete-row/{{uuid}}'.format(url_prefix))
    config.add_view(row_crud, attr='delete', route_name='{0}.rows.delete'.format(route_prefix),
                    permission='{0}.edit'.format(permission_prefix))
