## -*- coding: utf-8 -*-
## TODO: This function signature is getting out of hand...
<%def name="autocomplete(field_name, service_url, field_value=None, field_display=None, width='300px', select=None, selected=None, cleared=None, options={})">
  <div id="${field_name}-container" class="autocomplete-container">
    ${h.hidden(field_name, id=field_name, value=field_value)}
    ${h.text(field_name+'-textbox', id=field_name+'-textbox', value=field_display,
        class_='autocomplete-textbox', style='display: none;' if field_value else '')}
    <div id="${field_name}-display" class="autocomplete-display"${'' if field_value else ' style="display: none;"'|n}>
      <span>${field_display or ''}</span>
      <button type="button" id="${field_name}-change" class="autocomplete-change">Change</button>
    </div>
  </div>
  <script type="text/javascript">
    $(function() {
        $('#${field_name}-textbox').autocomplete({
            source: '${service_url}',
            autoFocus: true,
            % for key, value in options.items():
                ${key}: ${value},
            % endfor
            focus: function(event, ui) {
                return false;
            },
            % if select:
                select: ${select}
            % else:
                select: function(event, ui) {
                    $('#${field_name}').val(ui.item.value);
                    $('#${field_name}-display span:first').text(ui.item.label);
                    $('#${field_name}-textbox').hide();
                    $('#${field_name}-display').show();
                    % if selected:
                        ${selected}(ui.item.value, ui.item.label);
                    % endif
                    return false;
                }
            % endif
        });
        $('#${field_name}-change').click(function() {
            $('#${field_name}').val('');
            $('#${field_name}-display').hide();
            with ($('#${field_name}-textbox')) {
                val('');
                show();
                focus();
            }
            % if cleared:
                ${cleared}();
            % endif
        });
    });
  </script>
</%def>
