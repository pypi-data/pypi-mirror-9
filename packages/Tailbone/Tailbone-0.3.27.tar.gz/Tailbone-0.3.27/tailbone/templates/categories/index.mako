## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Categories</%def>

<%def name="context_menu_items()">
  % if request.has_perm('categories.create'):
      <li>${h.link_to("Create a new Category", url('category.create'))}</li>
  % endif
</%def>

${parent.body()}
