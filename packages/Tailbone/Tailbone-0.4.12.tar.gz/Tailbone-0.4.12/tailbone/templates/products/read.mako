## -*- coding: utf-8 -*-
<%inherit file="/products/crud.mako" />
<%namespace file="/forms/lib.mako" import="render_field_readonly" />

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">
    #product-main {
        width: 80%;
    }
    #product-image {
        float: left;
        margin-left: 300px;
    }
    .panel-wrapper {
        float: left;
        margin-right: 15px;
        min-width: 40%;
    }
  </style>
</%def>

<% product = form.fieldset.model %>

<%def name="render_organization_fields(form)">
    ${render_field_readonly(form.fieldset.department)}
    ${render_field_readonly(form.fieldset.subdepartment)}
    ${render_field_readonly(form.fieldset.category)}
    ${render_field_readonly(form.fieldset.family)}
    ${render_field_readonly(form.fieldset.report_code)}
</%def>

<%def name="render_price_fields(form)">
    ${render_field_readonly(form.fieldset.regular_price)}
    ${render_field_readonly(form.fieldset.current_price)}
    ${render_field_readonly(form.fieldset.current_price_ends)}
    ${render_field_readonly(form.fieldset.deposit_link)}
    ${render_field_readonly(form.fieldset.tax)}
</%def>

<%def name="render_flag_fields(form)">
    ${render_field_readonly(form.fieldset.weighed)}
    ${render_field_readonly(form.fieldset.discountable)}
    ${render_field_readonly(form.fieldset.special_order)}
    ${render_field_readonly(form.fieldset.organic)}
    ${render_field_readonly(form.fieldset.not_for_sale)}
    ${render_field_readonly(form.fieldset.deleted)}
</%def>

<%def name="render_movement_fields(form)">
    ${render_field_readonly(form.fieldset.last_sold)}
</%def>

<div class="form-wrapper">
  <ul class="context-menu">
    ${self.context_menu_items()}
  </ul>

  <div class="panel" id="product-main">
    <h2>Product</h2>
    <div class="panel-body">
      <div style="clear: none; float: left;">
        ${render_field_readonly(form.fieldset.upc)}
        ${render_field_readonly(form.fieldset.brand)}
        ${render_field_readonly(form.fieldset.description)}
        ${render_field_readonly(form.fieldset.unit_size)}
        ${render_field_readonly(form.fieldset.unit_of_measure)}
        ${render_field_readonly(form.fieldset.size)}
        ${render_field_readonly(form.fieldset.case_pack)}
      </div>
      % if image:
          ${h.image(image_url, "Product Image", id='product-image', path=image_path, use_pil=True)}
      % endif
    </div>
  </div>

  <div class="panel-wrapper"> <!-- left column -->

    <div class="panel">
      <h2>Pricing</h2>
      <div class="panel-body">
        ${self.render_price_fields(form)}
      </div>
    </div>

    <div class="panel">
      <h2>Flags</h2>
      <div class="panel-body">
        ${self.render_flag_fields(form)}
      </div>
    </div>

    ${self.extra_left_panels()}

  </div> <!-- left column -->

  <div class="panel-wrapper"> <!-- right column -->

    <div class="panel">
      <h2>Organization</h2>
      <div class="panel-body">
        ${self.render_organization_fields(form)}
      </div>
    </div>

    <div class="panel">
      <h2>Movement</h2>
      <div class="panel-body">
        ${self.render_movement_fields(form)}
      </div>
    </div>

    <div class="panel-grid" id="product-costs">
      <h2>Vendor Sources</h2>
      <div class="grid full hoverable no-border">
        <table>
          <thead>
            <th>Pref.</th>
            <th>Vendor</th>
            <th>Code</th>
            <th>Case Size</th>
            <th>Case Cost</th>
            <th>Unit Cost</th>
          </thead>
          <tbody>
            % for i, cost in enumerate(product.costs, 1):
                <tr class="${'odd' if i % 2 else 'even'}">
                  <td class="center">${'X' if cost.preference == 1 else ''}</td>
                  <td>${cost.vendor}</td>
                  <td class="center">${cost.code}</td>
                  <td class="center">${cost.case_size}</td>
                  <td class="right">${'$ %0.2f' % cost.case_cost if cost.case_cost is not None else ''}</td>
                  <td class="right">${'$ %0.4f' % cost.unit_cost if cost.unit_cost is not None else ''}</td>
                </tr>
            % endfor
          </tbody>
        </table>
      </div>
    </div>

    <div class="panel-grid" id="product-codes">
      <h2>Additional Lookup Codes</h2>
      <div class="grid full hoverable no-border">
        <table>
          <thead>
            <th>Code</th>
          </thead>
          <tbody>
            % for i, code in enumerate(product.codes, 1):
                <tr class="${'odd' if i % 2 else 'even'}">
                  <td>${code}</td>
                </tr>
            % endfor
          </tbody>
        </table>
      </div>
    </div>

    ${self.extra_right_panels()}

  </div> <!-- right column -->

  % if buttons:
      ${buttons|n}
  % endif
</div>

<%def name="extra_left_panels()"></%def>

<%def name="extra_right_panels()"></%def>
