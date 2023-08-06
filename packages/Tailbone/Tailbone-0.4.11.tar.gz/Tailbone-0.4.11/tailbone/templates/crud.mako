## -*- coding: utf-8 -*-
<%inherit file="/form.mako" />

<%def name="title()">${"New "+form.pretty_name if form.creating else form.pretty_name+' : '+capture(self.model_title)}</%def>

<%def name="model_title()">${h.literal(unicode(form.fieldset.model))}</%def>

<%def name="head_tags()">
  ${parent.head_tags()}
  <script type="text/javascript">
    $(function() {
        $('a.delete').click(function() {
            if (! confirm("Do you really wish to delete this object?")) {
                return false;
            }
        });
    });
  </script>
</%def>

${parent.body()}
