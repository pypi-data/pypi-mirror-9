## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Vendors</%def>

<%def name="context_menu_items()">
  % if request.has_perm('vendors.create'):
      <li>${h.link_to("Create a new Vendor", url('vendor.create'))}</li>
  % endif
</%def>

${parent.body()}
