## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Products", url('products'))}</li>
  % if form.readonly and request.has_perm('products.update'):
      <li>${h.link_to("Edit this Product", url('product.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to("View this Product", url('product.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
