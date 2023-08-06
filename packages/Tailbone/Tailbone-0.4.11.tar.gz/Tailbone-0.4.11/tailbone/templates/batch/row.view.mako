## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="title()">${batch_display} Row</%def>

<%def name="context_menu_items()">
      <li>${h.link_to("Back to {0}".format(batch_display), url('{0}.view'.format(route_prefix), uuid=row.batch_uuid))}</li>
</%def>

${parent.body()}
