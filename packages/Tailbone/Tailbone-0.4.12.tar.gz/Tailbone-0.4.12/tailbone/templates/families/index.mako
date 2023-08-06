## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Families</%def>

<%def name="context_menu_items()">
  % if request.has_perm('families.create'):
      <li>${h.link_to("Create a new Family", url('family.create'))}</li>
  % endif
</%def>

${parent.body()}
