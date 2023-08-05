## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Subdepartments</%def>

<%def name="context_menu_items()">
  % if request.has_perm('subdepartments.create'):
      <li>${h.link_to("Create a new Subdepartment", url('subdepartment.create'))}</li>
  % endif
</%def>

${parent.body()}
