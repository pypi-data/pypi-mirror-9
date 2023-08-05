## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Subdepartments", url('subdepartments'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Subdepartment", url('subdepartment.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Subdepartment", url('subdepartment.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
