## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Customer Groups</%def>

<%def name="context_menu_items()">
  % if request.has_perm('customer_groups.create'):
      <li>${h.link_to("Create a new Customer Group", url('customer_group.create'))}</li>
  % endif
</%def>

${parent.body()}
