## -*- coding: utf-8 -*-
<%inherit file="/products/crud.mako" />

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">
    #product-image {
        float: left;
        margin-left: 250px;
        margin-top: 40px;
    }
  </style>
</%def>

<div class="form-wrapper">
  <ul class="context-menu">
    ${self.context_menu_items()}
  </ul>

  ${form.render()|n}

  % if image:
      ${h.image(image_url, "Product Image", id='product-image', path=image_path, use_pil=True)}
  % endif
</div>

<% product = form.fieldset.model %>

<div id="product-codes">
  <h2>Product Codes:</h2>
  % if product.codes:
      <div class="grid hoverable">
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
  % else:
      <p>None on file.</p>
  % endif
</div>

<div id="product-costs">
  <h2>Product Costs:</h2>
  % if product.costs:
      <div class="grid hoverable">
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
  % else:
      <p>None on file.</p>
  % endif
</div>
