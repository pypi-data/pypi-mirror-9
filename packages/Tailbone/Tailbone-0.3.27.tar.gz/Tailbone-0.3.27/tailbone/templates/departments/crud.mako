## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Departments", url('departments'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Department", url('department.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Department", url('department.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
