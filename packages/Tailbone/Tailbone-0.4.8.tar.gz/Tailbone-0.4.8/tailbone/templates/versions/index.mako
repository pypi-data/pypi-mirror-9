## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">${model_title} Change History</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to all {0}".format(model_title_plural), url(route_model_list))}</li>
  <li>${h.link_to("Back to current {0}".format(model_title), url(route_model_view, uuid=model_instance.uuid))}</li>
</%def>

<%def name="form()">
    <h2>Changes for ${model_title}:&nbsp; ${model_instance}</h2>
</%def>

${parent.body()}
