## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Report Codes", url('reportcodes'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Report Code", url('reportcode.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Report Code", url('reportcode.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
