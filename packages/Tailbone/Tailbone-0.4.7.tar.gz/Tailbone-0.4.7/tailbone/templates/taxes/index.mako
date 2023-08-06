## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Taxes</%def>

<%def name="context_menu_items()">
  % if request.has_perm('taxes.create'):
      <li>${h.link_to("Create a new Tax", url('tax.new'))}</li>
  % endif
</%def>

${parent.body()}
