## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Departments</%def>

<%def name="context_menu_items()">
  % if request.has_perm('departments.create'):
      <li>${h.link_to("Create a new Department", url('department.create'))}</li>
  % endif
</%def>

${parent.body()}
