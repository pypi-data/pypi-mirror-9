## -*- coding: utf-8 -*-
<%inherit file="/batches/params.mako" />

<%def name="batch_params()">

  <div class="field-wrapper">
    <label for="profile">Label Type</label>
    <div class="field">
      ${h.select('profile', None, label_profiles)}
    </div>
  </div>

  <div class="field-wrapper">
    <label for="quantity">Quantity</label>
    <div class="field">${h.text('quantity', value=1)}</div>
  </div>

</%def>

${parent.body()}
