## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Families", url('families'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Family", url('family.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Family", url('family.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
