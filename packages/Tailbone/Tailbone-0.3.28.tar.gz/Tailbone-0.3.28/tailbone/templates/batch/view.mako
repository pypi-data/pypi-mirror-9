## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="title()">View ${batch_display}</%def>

<%def name="head_tags()">
    <script type="text/javascript">
      $(function() {
          $('#rows-wrapper').load('${url('{0}.rows'.format(route_prefix), uuid=batch.uuid)}', function() {
              // TODO: It'd be nice if we didn't have to do this here.
              $(this).find('button').button();
              $(this).find('input[type=submit]').button();
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
        % if request.has_perm('{0}.edit'.format(permission_prefix)):
            ## <li>${h.link_to("Edit this {0}".format(batch_display), url('{0}.edit'.format(route_prefix), uuid=batch.uuid))}</li>
            % if batch.refreshable:
                <li>${h.link_to("Refresh Data for this {0}".format(batch_display), url('{0}.refresh'.format(route_prefix), uuid=batch.uuid))}</li>
            % endif
        % endif
        % if request.has_perm('{0}.execute'.format(permission_prefix)):
            <li>${h.link_to("Execute this {0}".format(batch_display), url('{0}.execute'.format(route_prefix), uuid=batch.uuid))}</li>
        % endif
    % endif
    % if request.has_perm('{0}.delete'.format(permission_prefix)):
        <li>${h.link_to("Delete this {0}".format(batch_display), url('{0}.delete'.format(route_prefix), uuid=batch.uuid))}</li>
    % endif
  </ul>

  ${form.render()|n}

</div>

<div id="rows-wrapper"></div>
