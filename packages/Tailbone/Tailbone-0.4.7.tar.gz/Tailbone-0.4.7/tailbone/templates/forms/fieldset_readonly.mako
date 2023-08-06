## -*- coding: utf-8 -*-
<%namespace file="/forms/lib.mako" import="render_field_readonly" />
<div class="fieldset">
  % for field in fieldset.render_fields.itervalues():
      ${render_field_readonly(field)}
  % endfor
</div>
