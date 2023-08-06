## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Products</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <style type="text/css">

    table.grid-header td.tools table {
        margin-left: auto;
    }

    table.grid-header td.tools table th,
    table.grid-header td.tools table td {
        padding: 0px;
        text-align: left;
    }

    table.grid-header td.tools table #label-quantity {
        text-align: right;
        width: 30px;
    }

    div.grid table tbody td.size,
    div.grid table tbody td.regular_price_uuid,
    div.grid table tbody td.current_price_uuid {
        padding-right: 6px;
        text-align: right;
    }
    
    div.grid table tbody td.labels {
        text-align: center;
    }
    
  </style>
  % if label_profiles and request.has_perm('products.print_labels'):
      <script language="javascript" type="text/javascript">

        $(function() {
            $('div.grid a.print-label').live('click', function() {
                var quantity = $('#label-quantity').val();
                if (isNaN(quantity)) {
                    alert("You must provide a valid label quantity.");
                    $('#label-quantity').select();
                    $('#label-quantity').focus();
                } else {
                    $.ajax({
                        url: '${url('products.print_labels')}',
                        data: {
                            'product': get_uuid(this),
                            'profile': $('#label-profile').val(),
                            'quantity': quantity,
                        },
                        success: function(data) {
                            if (data.error) {
                                alert("An error occurred while attempting to print:\n\n" + data.error);
                            } else if (quantity == '1') {
                                alert("1 label has been printed.");
                            } else {
                                alert(quantity + " labels have been printed.");
                            }
                        },
                    });
                }
                return false;
            });
        });

      </script>
  % endif
</%def>

<%def name="tools()">
  % if label_profiles and request.has_perm('products.print_labels'):
      <table>
        <thead>
          <tr>
            <td>Label</td>
            <td>Qty.</td>
          </tr>
        </thead>
        <tbody>
          <td>
            <select name="label-profile" id="label-profile">
              % for profile in label_profiles:
                  <option value="${profile.uuid}">${profile.description}</option>
              % endfor
            </select>
          </td>
          <td>
            <input type="text" name="label-quantity" id="label-quantity" value="1" />
          </td>
        </tbody>
      </table>
  % endif
</%def>

<%def name="context_menu_items()">
  % if request.has_perm('products.create'):
      <li>${h.link_to("Create a new Product", url('product.create'))}</li>
  % endif
  % if request.has_perm('batches.create'):
      <li>${h.link_to("Create Batch from Results", url('products.create_batch'))}</li>
  % endif
</%def>

${parent.body()}
