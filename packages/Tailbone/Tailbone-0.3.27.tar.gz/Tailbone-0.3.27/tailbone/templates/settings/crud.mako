## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Settings", url('settings'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Setting", url('settings.edit', name=form.fieldset.model.name))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Setting", url('settings.view', name=form.fieldset.model.name))}</li>
  % endif
</%def>

${parent.body()}
