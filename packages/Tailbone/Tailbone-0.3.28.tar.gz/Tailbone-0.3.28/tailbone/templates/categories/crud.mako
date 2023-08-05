## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Categories", url('categories'))}</li>
  % if form.readonly:
      <li>${h.link_to("Edit this Category", url('category.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Category", url('category.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
