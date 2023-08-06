## -*- coding: utf-8 -*-
<%inherit file="/batches/crud.mako" />

<%def name="context_menu_items()">
  ${parent.context_menu_items()}
  <li>${h.link_to("Edit this Batch", url('batch.update', uuid=form.fieldset.model.uuid))}</li>
  <li>${h.link_to("Delete this Batch", url('batch.delete', uuid=form.fieldset.model.uuid))}</li>
</%def>

${parent.body()}

<% batch = form.fieldset.model %>

<h2>Columns</h2>

<div class="grid full hoverable">
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>SIL Name</th>
        <th>Display Name</th>
        <th>Description</th>
        <th>Data Type</th>
        <th>Visible</th>
      </tr>
    </thead>
    <tbody>
      % for i, column in enumerate(batch.columns, 1):
          <tr class="${'odd' if i % 2 else 'even'}">
            <td>${column.name}</td>
            <td>${column.sil_name}</td>
            <td>${column.display_name}</td>
            <td>${column.description}</td>
            <td>${column.data_type}</td>
            <td>${column.visible}</td>
          </tr>
      % endfor
    </tbody>
  </table>
</div>
