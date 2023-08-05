## -*- coding: utf-8 -*-
<div class="form">
  ${h.form(form.action_url, enctype='multipart/form-data')}

  ${form.fieldset.render()|n}

  <div class="buttons">
    ${h.submit('create', form.create_label if form.creating else form.update_label)}
    % if form.creating and form.allow_successive_creates:
        ${h.submit('create_and_continue', form.successive_create_label)}
    % endif
    <a href="${form.cancel_url}">Cancel</a>
  </div>

  ${h.end_form()}
</div>
