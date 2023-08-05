## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">Printer Settings</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Label Profiles", url('label_profiles'))}</li>
  <li>${h.link_to("View this Label Profile", url('label_profile.read', uuid=profile.uuid))}</li>
  <li>${h.link_to("Edit this Label Profile", url('label_profile.update', uuid=profile.uuid))}</li>
</%def>

<div class="form-wrapper">

  <ul class="context-menu">
    ${self.context_menu_items()}
  </ul>

  <div class="form">

    <div class="field-wrapper">
      <label>Label Profile</label>
      <div class="field">${profile.description}</div>
    </div>

    <div class="field-wrapper">
      <label>Printer Spec</label>
      <div class="field">${profile.printer_spec}</div>
    </div>

    ${h.form(request.current_route_url())}

    % for name, display in printer.required_settings.iteritems():
        <div class="field-wrapper">
          <label for="${name}">${display}</label>
          <div class="field">
            ${h.text(name, value=profile.get_printer_setting(name))}
          </div>
        </div>
    % endfor

    <div class="buttons">
      ${h.submit('update', "Update")}
      <button type="button" onclick="location.href = '${url('label_profile.read', uuid=profile.uuid)}';">Cancel</button>
    </div>

    ${h.end_form()}
  </div>

</div>
