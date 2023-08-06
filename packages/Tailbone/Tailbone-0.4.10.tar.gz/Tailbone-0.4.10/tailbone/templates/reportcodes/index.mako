## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Report Codes</%def>

<%def name="context_menu_items()">
  % if request.has_perm('reportcodes.create'):
      <li>${h.link_to("Create a new Report Code", url('reportcode.create'))}</li>
  % endif
</%def>

${parent.body()}
