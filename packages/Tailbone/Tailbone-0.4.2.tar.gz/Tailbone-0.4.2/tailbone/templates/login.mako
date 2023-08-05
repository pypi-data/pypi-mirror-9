## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">Login</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  ${h.javascript_link(request.static_url('tailbone:static/js/login.js'))}
  ${h.stylesheet_link(request.static_url('tailbone:static/css/login.css'))}
</%def>

<%def name="logo()">
    ${h.image(request.static_url('tailbone:static/img/home_logo.png'), "Rattail Logo", id='logo')}
</%def>

${self.logo()}

<div class="form">
  ${h.form('')}
  <input type="hidden" name="referrer" value="${referrer}" />

  % if error:
      <div class="error">${error}</div>
  % endif

  <div class="field-wrapper">
    <label for="username">Username</label>
    <input type="text" name="username" id="username" value="" />
  </div>

  <div class="field-wrapper">
    <label for="password">Password</label>
    <input type="password" name="password" id="password" value="" />
  </div>

  <div class="buttons">
    ${h.submit('submit', "Login")}
    <input type="reset" value="Reset" />
  </div>

  ${h.end_form()}
</div>
