## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Stores</%def>

<%def name="context_menu_items()">
  % if request.has_perm('stores.create'):
      <li>${h.link_to("Create a new Store", url('store.create'))}</li>
  % endif
</%def>

${parent.body()}
