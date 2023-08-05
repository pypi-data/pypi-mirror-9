## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">${batch_display_plural}</%def>

<%def name="context_menu_items()">
  % if request.has_perm('{0}.create'.format(permission_prefix)):
      <li>${h.link_to("Create a new {0}".format(batch_display), url('{0}.create'.format(route_prefix)))}</li>
  % endif
</%def>

${parent.body()}
