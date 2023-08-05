## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Batch Rows : ${batch.description}</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <script language="javascript" type="text/javascript">

    $(function() {

        $('#delete-results').click(function() {
            var msg = "This will delete all rows matching the current search.\n\n"
                + "PLEASE NOTE that this may include some rows which are not visible "
                + "on your screen.\n(I.e., if there is more than one \"page\" of results.)\n\n"
                + "Are you sure you wish to delete these rows?";
            if (confirm(msg)) {
                disable_button(this, "Deleting rows");
                location.href = '${url('batch.rows.delete', uuid=batch.uuid)}';
            }
        });

        $('#execute-batch').click(function() {
            if (confirm("Are you sure you wish to execute this batch?")) {
                disable_button(this, "Executing batch");
                location.href = '${url('batch.execute', uuid=batch.uuid)}';
            }
        });

    });

  </script>
</%def>

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Batches", url('batches'))}</li>
  <li>${h.link_to("Back to Batch", url('batch.read', uuid=batch.uuid))}</li>
</%def>

<%def name="tools()">
  <div class="buttons">
    <button type="button" id="delete-results">Delete Results</button>
    <button type="button" id="execute-batch">Execute Batch</button>
  </div>
</%def>

${parent.body()}
