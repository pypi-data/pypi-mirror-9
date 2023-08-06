## -*- coding: utf-8 -*-
<div class="grid-wrapper">

  <table class="grid-header">
    <tr>
      <td rowspan="2" class="form">
        ${search.render()}
      </td>
    </tr>
    <tr>
      <td class="tools">
        ## TODO: Fix this check for edit mode.
        % if not batch.executed and request.referrer.endswith('/edit'):
            <p>${h.link_to("Delete all rows matching current search", url('{0}.rows.bulk_delete'.format(route_prefix), uuid=batch.uuid))}</p>
        % endif
      </td>
    </tr>
  </table>

  ${grid}

</div>
