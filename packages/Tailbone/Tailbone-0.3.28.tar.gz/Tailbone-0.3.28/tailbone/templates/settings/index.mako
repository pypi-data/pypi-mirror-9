## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Settings</%def>

<%def name="context_menu_items()">
  % if request.has_perm('settings.create'):
      <li>${h.link_to("Create a new Setting", url('settings.create'))}</li>
  % endif
</%def>

${parent.body()}
