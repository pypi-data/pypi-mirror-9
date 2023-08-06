## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Employees", url('employees'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Employee", url('employee.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Employee", url('employee.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
