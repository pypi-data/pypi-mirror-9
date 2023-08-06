## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">${model_title} Version Details</%def>

<%def name="head_tags()">
    <style type="text/css">
      td.oldvalue {
          background-color: #fcc;
      }
      td.newvalue {
          background-color: #cfc;
      }
    </style>
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to all {0}".format(model_title_plural), url(route_model_list))}</li>
  <li>${h.link_to("Back to current {0}".format(model_title), url(route_model_view, uuid=model_instance.uuid))}</li>
  <li>${h.link_to("Back to Version History", url('{0}.versions'.format(route_prefix), uuid=model_instance.uuid))}</li>
</%def>

<div class="form-wrapper">

  <ul class="context-menu">
    ${self.context_menu_items()}
  </ul>

  <div class="form">

    <div>
      % if previous_transaction or next_transaction:
          % if previous_transaction:
              ${h.link_to("<< older version", url('{0}.version'.format(route_prefix), uuid=model_instance.uuid, transaction_id=previous_transaction.id))}
          % else:
              <span>(oldest version)</span>
          % endif
          &nbsp; | &nbsp;
          % if next_transaction:
              ${h.link_to("newer version >>", url('{0}.version'.format(route_prefix), uuid=model_instance.uuid, transaction_id=next_transaction.id))}
          % else:
              <span>(newest version)</span>
          % endif
      % else:
          <span>(only version)</span>
      % endif
    </div>

    <div class="fieldset">

      <div class="field-wrapper">
        <label>When:</label>
        <div class="field">${h.pretty_datetime(request.rattail_config, transaction.issued_at)}</div>
      </div>
      <div class="field-wrapper">
        <label>Who:</label>
        <div class="field">${transaction.user or "(unknown / system)"}</div>
      </div>
      <div class="field-wrapper">
        <label>Where:</label>
        <div class="field">${transaction.remote_addr}</div>
      </div>

      % for ver in versions:
          
          <div class="field-wrapper">
            <label>What:</label>
            <div class="field" style="font-weight: bold;">${ver.version_parent.__class__.__name__}:&nbsp; ${ver.version_parent}</div>
          </div>

          <div class="field-wrapper">
            <label>Changes:</label>
            <div class="field">
              <div class="grid">
                <table>
                  <thead>
                    <tr>
                      <th>Field</th>
                      <th>Old Value</th>
                      <th>New Value</th>
                    </tr>
                  </thead>
                  <tbody>
                    % for key in sorted(ver.changeset):
                        <tr>
                          <td>${key}</td>
                          <td class="oldvalue">${ver.changeset[key][0]}</td>
                          <td class="newvalue">${ver.changeset[key][1]}</td>
                        </tr>
                    % endfor
                  </tbody>
                </table>
              </div>
            </div>
          </div>

      % endfor

    </div>

  </div>

</div>
