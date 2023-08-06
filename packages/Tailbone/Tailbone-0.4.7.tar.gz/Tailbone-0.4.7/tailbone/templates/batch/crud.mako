## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="title()">${"View" if form.readonly else "Edit"} ${batch_display}</%def>

<%def name="head_tags()">
    <script type="text/javascript">
      $(function() {
          $('#rows-wrapper').load('${url('{0}.rows'.format(route_prefix), uuid=batch.uuid)}', function() {
              // TODO: It'd be nice if we didn't have to do this here.
              $(this).find('button').button();
              $(this).find('input[type=submit]').button();
          });
          $('#save-refresh').click(function() {
              $('#batch-form').append($('<input type="hidden" name="refresh" value="true" />'));
              $('#batch-form').submit();
          });
      });
    </script>
    <style type="text/css">
      #rows-wrapper {
          margin-top: 10px;
      }
      .grid tr.notice.odd {
          background-color: #fe8;
      }
      .grid tr.notice.even {
          background-color: #fd6;
      }
      .grid tr.notice.hovering {
          background-color: #ec7;
      }
      .grid tr.warning.odd {
          background-color: #ebb;
      }
      .grid tr.warning.even {
          background-color: #fcc;
      }
      .grid tr.warning.hovering {
          background-color: #daa;
      }
    </style>
</%def>

<div class="form-wrapper">

  <ul class="context-menu">
    <li>${h.link_to("Back to {0}".format(batch_display_plural), url(route_prefix))}</li>
    % if not batch.executed:
        % if form.updating:
            <li>${h.link_to("View this {0}".format(batch_display), url('{0}.view'.format(route_prefix), uuid=batch.uuid))}</li>
        % endif
        % if form.readonly and request.has_perm('{0}.edit'.format(permission_prefix)):
            <li>${h.link_to("Edit this {0}".format(batch_display), url('{0}.edit'.format(route_prefix), uuid=batch.uuid))}</li>
        % endif
    % endif
    % if request.has_perm('{0}.delete'.format(permission_prefix)):
        <li>${h.link_to("Delete this {0}".format(batch_display), url('{0}.delete'.format(route_prefix), uuid=batch.uuid))}</li>
    % endif
  </ul>

  ${form.render(form_id='batch-form', buttons=capture(buttons))|n}

</div>

<%def name="buttons()">
    <div class="buttons">
      % if not form.readonly and batch.refreshable:
          ${h.submit('save-refresh', "Save & Refresh Data")}
      % endif
      % if not batch.executed and request.has_perm('{0}.execute'.format(permission_prefix)):
          ## ${h.link_to(execute_title, url('{0}.execute'.format(route_prefix), uuid=batch.uuid))}
          <button type="button" onclick="location.href = '${url('{0}.execute'.format(route_prefix), uuid=batch.uuid)}';">${execute_title}</button>
      % endif
    </div>
</%def>

<div id="rows-wrapper"></div>
