## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to People", url('people'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Person", url('person.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Person", url('person.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
