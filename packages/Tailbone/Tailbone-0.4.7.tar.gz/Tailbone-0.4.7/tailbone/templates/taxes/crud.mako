## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Taxes", url('taxes'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Tax", url('tax.edit', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Tax", url('tax.view', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
