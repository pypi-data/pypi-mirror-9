## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Customers", url('customers'))}</li>
  % if form.readonly and request.has_perm('customers.update'):
      <li>${h.link_to("Edit this Customer", url('customer.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Customer", url('customer.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
