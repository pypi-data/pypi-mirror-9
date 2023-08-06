## -*- coding: utf-8 -*-
<%inherit file="/labels/profiles/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Label Profiles", url('label_profiles'))}</li>
  % if form.readonly and request.has_perm('label_profiles.update'):
      <% profile = form.fieldset.model %>
      <% printer = profile.get_printer(request.rattail_config) %>
      <li>${h.link_to("Edit this Label Profile", url('label_profile.update', uuid=form.fieldset.model.uuid))}</li>
      % if printer and printer.required_settings:
          <li>${h.link_to("Edit Printer Settings", url('label_profile.printer_settings', uuid=profile.uuid))}</li>
      % endif
  % endif
  % if version_count is not Undefined and request.has_perm('labelprofile.versions.view'):
      <li>${h.link_to("View Change History ({0})".format(version_count), url('labelprofile.versions', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}

<% profile = form.fieldset.model %>
<% printer = profile.get_printer(request.rattail_config) %>

% if printer and printer.required_settings:
    <h2>Printer Settings</h2>

    <div class="form">
      % for name, display in printer.required_settings.iteritems():
          <div class="field-wrapper">
            <label>${display}</label>
            <div class="field">${profile.get_printer_setting(name) or ''}</div>
          </div>
      % endfor
    </div>

% endif
