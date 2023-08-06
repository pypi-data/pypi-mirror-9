## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="title()">Upload ${batch_display}</%def>

<%def name="context_menu_items()">
  % if request.has_perm('{0}.view'.format(permission_prefix)):
      <li>${h.link_to("Back to {0}".format(batch_display_plural), url(route_prefix))}</li>
  % endif
</%def>

${parent.body()}
