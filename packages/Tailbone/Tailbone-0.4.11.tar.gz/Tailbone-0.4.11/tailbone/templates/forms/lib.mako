## -*- coding: utf-8 -*-

<%def name="render_field_readonly(field)">
    % if field.requires_label:
        <div class="field-wrapper ${field.name}">
          ${field.label_tag()|n}
          <div class="field">
            ${field.render_readonly()}
          </div>
        </div>
    % endif
</%def>
