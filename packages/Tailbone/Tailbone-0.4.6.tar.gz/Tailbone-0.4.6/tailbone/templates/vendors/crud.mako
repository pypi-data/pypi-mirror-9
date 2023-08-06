## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Vendors", url('vendors'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Vendor", url('vendor.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Vendor", url('vendor.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
  % if version_count is not Undefined and request.has_perm('vendor.versions.view'):
      <li>${h.link_to("View Change History ({0})".format(version_count), url('vendor.versions', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
