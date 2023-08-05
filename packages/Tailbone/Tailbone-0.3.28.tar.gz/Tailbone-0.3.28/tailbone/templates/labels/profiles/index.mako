## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Label Profiles</%def>

<%def name="context_menu_items()">
  % if request.has_perm('label_profiles.create'):
      <li>${h.link_to("Create a new Label Profile", url('label_profile.create'))}</li>
  % endif
</%def>

${parent.body()}
