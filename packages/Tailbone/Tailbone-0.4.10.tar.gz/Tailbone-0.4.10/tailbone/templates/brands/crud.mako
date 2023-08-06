## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Brands", url('brands'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Brand", url('brand.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Brand", url('brand.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
  % if version_count is not Undefined and request.has_perm('brand.versions.view'):
      <li>${h.link_to("View Change History ({0})".format(version_count), url('brand.versions', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
