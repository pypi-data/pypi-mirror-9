## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">Home</%def>

<div style="text-align: center;">
  ${h.image(request.static_url('tailbone:static/img/home_logo.png'), "Rattail Logo")}
  <h1>Welcome to Tailbone</h1>
</div>
