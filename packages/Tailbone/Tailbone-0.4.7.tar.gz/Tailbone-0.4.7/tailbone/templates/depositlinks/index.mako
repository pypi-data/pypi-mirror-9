## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Deposit Links</%def>

<%def name="context_menu_items()">
  % if request.has_perm('depositlinks.create'):
      <li>${h.link_to("Create a new Deposit Link", url('depositlink.new'))}</li>
  % endif
</%def>

${parent.body()}
