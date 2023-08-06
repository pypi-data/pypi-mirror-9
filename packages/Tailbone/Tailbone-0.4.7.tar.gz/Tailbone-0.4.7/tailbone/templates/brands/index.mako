## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Brands</%def>

<%def name="context_menu_items()">
  % if request.has_perm('brands.create'):
      <li>${h.link_to("Create a new Brand", url('brand.create'))}</li>
  % endif
</%def>

${parent.body()}
