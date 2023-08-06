## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Stores", url('stores'))}</li>
  % if form.readonly and request.has_perm('stores.update'):
      <li>${h.link_to("Edit this Store", url('store.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Store", url('store.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
