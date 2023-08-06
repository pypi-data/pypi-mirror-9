## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to("Back to Batches", url('batches'))}</li>
  <li>${h.link_to("View Batch Rows", url('batch.rows', uuid=form.fieldset.model.uuid))}</li>
  % if not form.readonly:
      <li>${h.link_to("View this Batch", url('batch.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
