## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">

    div.form div.field-wrapper.format textarea {
        font-size: 120%;
        font-family: monospace;
        width: auto;
    }

  </style>
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Label Profiles", url('label_profiles'))}</li>
  % if form.updating:
      <% profile = form.fieldset.model %>
      <% printer = profile.get_printer(request.rattail_config) %>
      % if printer and printer.required_settings:
          <li>${h.link_to("Edit Printer Settings", url('label_profile.printer_settings', uuid=profile.uuid))}</li>
      % endif
      <li>${h.link_to("View this Label Profile", url('label_profile.read', uuid=profile.uuid))}</li>
  % endif
</%def>

${parent.body()}
