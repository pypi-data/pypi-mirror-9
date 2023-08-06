## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Batch", url('batch.read', uuid=form.fieldset.model.batch.uuid))}</li>
  <li>${h.link_to("Back to Batch Rows", url('batch.rows', uuid=form.fieldset.model.batch.uuid))}</li>
</%def>

${parent.body()}
