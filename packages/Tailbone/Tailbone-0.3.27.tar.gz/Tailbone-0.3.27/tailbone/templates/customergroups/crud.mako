## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Customer Groups", url('customer_groups'))}</li>
  % if form.readonly and request.has_perm('customer_groups.update'):
      <li>${h.link_to("Edit this Customer Group", url('customer_group.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Customer Group", url('customer_group.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
