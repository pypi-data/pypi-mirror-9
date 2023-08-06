## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Deposit Links", url('depositlinks'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Deposit Link", url('depositlink.edit', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Deposit Link", url('depositlink.view', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
