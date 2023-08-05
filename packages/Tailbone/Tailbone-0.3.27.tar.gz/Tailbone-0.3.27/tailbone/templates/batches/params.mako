## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="title()">Batch Parameters</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <script language="javascript" type="text/javascript">

    $(function() {

        $('#create-batch').click(function() {
            disable_button(this, "Creating batch");
            disable_button('#cancel');
            $('form').submit();
        });

    });

  </script>
</%def>

<%def name="batch_params()"></%def>

<p>Please provide the following values for your new batch:</p>
<br />

<div class="form">

  ${h.form(request.get_referrer())}
  ${h.hidden('provider', value=provider)}
  ${h.hidden('params', value='True')}

  ${self.batch_params()}

  <div class="buttons">
    <button type="button" id="create-batch">Create Batch</button>
    <button type="button" id="cancel" onclick="location.href = '${request.get_referrer()}';">Cancel</button>
  </div>

  ${h.end_form()}

</div>
