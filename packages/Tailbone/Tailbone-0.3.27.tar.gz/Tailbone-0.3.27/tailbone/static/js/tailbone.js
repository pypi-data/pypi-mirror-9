
/************************************************************
 *
 * tailbone.js
 *
 ************************************************************/


/*
 * Initialize the disabled filters array.  This is populated from within the
 * /grids/search.mako template.
 */
var filters_to_disable = [];


/*
 * Disables options within the "add filter" dropdown which correspond to those
 * filters already being displayed.  Called from /grids/search.mako template.
 */
function disable_filter_options() {
    while (filters_to_disable.length) {
        var filter = filters_to_disable.shift();
        var option = $('#add-filter option[value="' + filter + '"]');
        option.attr('disabled', 'disabled');
    }
}


/*
 * Convenience function to disable a form button.
 */
function disable_button(button, label) {
    if (label) {
        $(button).html(label + ", please wait...");
    }
    $(button).attr('disabled', 'disabled');
}


/*
 * Load next / previous page of results to grid.  This function is called on
 * the click event from the pager links, via inline script code.
 */
function grid_navigate_page(link, url) {
    var wrapper = $(link).parents('div.grid-wrapper');
    var grid = wrapper.find('div.grid');
    wrapper.mask("Loading...");
    $.get(url, function(data) {
        wrapper.unmask();
        grid.replaceWith(data);
    });
}


/*
 * Fetch the UUID value associated with a table row.
 */
function get_uuid(obj) {
    obj = $(obj);
    if (obj.attr('uuid')) {
        return obj.attr('uuid');
    }
    var tr = obj.parents('tr:first');
    if (tr.attr('uuid')) {
        return tr.attr('uuid');
    }
    return undefined;
}


/*
 * get_dialog(id, callback)
 *
 * Returns a <DIV> element suitable for use as a jQuery dialog.
 *
 * ``id`` is used to construct a proper ID for the element and allows the
 * dialog to be resused if possible.
 *
 * ``callback``, if specified, should be a callback function for the dialog.
 * This function will be called whenever the dialog has been closed
 * "successfully" (i.e. data submitted) by the user, and should accept a single
 * ``data`` object which is the JSON response returned by the server.
 */

function get_dialog(id, callback) {
    var dialog = $('#'+id+'-dialog');
    if (! dialog.length) {
        dialog = $('<div class="dialog" id="'+id+'-dialog"></div>');
    }
    if (callback) {
        dialog.attr('callback', callback);
    }
    return dialog;
}


$(function() {

    /*
     * Initialize the menu bar.
     */
    $('ul.menubar').menubar({
        buttons: true,
        menuIcon: true,
        autoExpand: true
    });

    /*
     * Fix buttons.
     */
    $('button').button();
    $('input[type=submit]').button();
    $('input[type=reset]').button();

    /*
     * When filter labels are clicked, (un)check the associated checkbox.
     */
    $('div.grid-wrapper div.filter label').on('click', function() {
        var checkbox = $(this).prev('input[type="checkbox"]');
        if (checkbox.prop('checked')) {
            checkbox.prop('checked', false);
            return false;
        }
        checkbox.prop('checked', true);
    });

    /*
     * When a new filter is selected in the "add filter" dropdown, show it in
     * the UI.  This selects the filter's checkbox and puts focus to its input
     * element.  If all available filters have been displayed, the "add filter"
     * dropdown will be hidden.
     */
    $('#add-filter').on('change', function() {
        var select = $(this);
        var filters = select.parents('div.filters:first');
        var filter = filters.find('#filter-' + select.val());
        var checkbox = filter.find('input[type="checkbox"]:first');
        var input = filter.find(':last-child');

        checkbox.prop('checked', true);
        filter.show();
        input.select();
        input.focus();

        filters.find('input[type="submit"]').show();
        filters.find('button[type="reset"]').show();

        select.find('option:selected').attr('disabled', true);
        select.val('add a filter');
        if (select.find('option:enabled').length == 1) {
            select.hide();
        }
    });

    /*
     * When user clicks the grid filters search button, perform the search in
     * the background and reload the grid in-place.
     */
    $('div.filters form').submit(function() {
        var form = $(this);
        var wrapper = form.parents('div.grid-wrapper');
        var grid = wrapper.find('div.grid');
        var data = form.serializeArray();
        data.push({name: 'partial', value: true});
        wrapper.mask("Loading...");
        $.get(grid.attr('url'), data, function(data) {
            wrapper.unmask();
            grid.replaceWith(data);
        });
        return false;
    });

    /*
     * When user clicks the grid filters reset button, manually clear all
     * filter input elements, and submit a new search.
     */
    $('div.filters form button[type="reset"]').click(function() {
        var form = $(this).parents('form');
        form.find('div.filter').each(function() {
            $(this).find('div.value input').val('');
        });
        form.submit();
        return false;
    });

    $('div.grid-wrapper').on('click', 'div.grid th.sortable a', function() {
        var th = $(this).parent();
        var wrapper = th.parents('div.grid-wrapper');
        var grid = wrapper.find('div.grid');
        var data = {
            sort: th.attr('field'),
            dir: (th.hasClass('sorted') && th.hasClass('asc')) ? 'desc' : 'asc',
            page: 1,
            partial: true
        };
        wrapper.mask("Loading...");
        $.get(grid.attr('url'), data, function(data) {
            wrapper.unmask();
            grid.replaceWith(data);
        });
        return false;
    });

    $('#body').on('mouseenter', 'div.grid.hoverable table tbody tr', function() {
        $(this).addClass('hovering');
    });

    $('#body').on('mouseleave', 'div.grid.hoverable table tbody tr', function() {
        $(this).removeClass('hovering');
    });

    $('div.grid-wrapper').on('click', 'div.grid table tbody td.view', function() {
        var url = $(this).attr('url');
        if (url) {
            location.href = url;
        }
    });

    $('div.grid-wrapper').on('click', 'div.grid table tbody td.edit', function() {
        var url = $(this).attr('url');
        if (url) {
            location.href = url;
        }
    });

    $('div.grid-wrapper').on('click', 'div.grid table tbody td.delete', function() {
        var url = $(this).attr('url');
        if (url) {
            if (confirm("Do you really wish to delete this object?")) {
                location.href = url;
            }
        }
    });

    $('div.grid-wrapper').on('change', 'div.grid div.pager select#grid-page-count', function() {
        var select = $(this);
        var wrapper = select.parents('div.grid-wrapper');
        var grid = wrapper.find('div.grid');
        var data = {
            per_page: select.val(),
            partial: true
        };
        wrapper.mask("Loading...");
        $.get(grid.attr('url'), data, function(data) {
            wrapper.unmask();
            grid.replaceWith(data);
        });

    });

    /*
     * Whenever the "change" button is clicked within the context of an
     * autocomplete field, hide the static display and show the autocomplete
     * textbox.
     */
    $('div.autocomplete-container button.autocomplete-change').click(function() {
        var container = $(this).parents('div.autocomplete-container');
        var textbox = container.find('input.autocomplete-textbox');

        container.find('input[type="hidden"]').val('');
        container.find('div.autocomplete-display').hide();

        textbox.val('');
        textbox.show();
        textbox.select();
        textbox.focus();
    });

    /*
     * Add "check all" functionality to tables with checkboxes.
     */
    $('body').on('click', 'div.grid table thead th.checkbox input[type="checkbox"]', function() {
        var table = $(this).parents('table:first');
        var checked = $(this).prop('checked');
        table.find('tbody tr').each(function() {
            $(this).find('td.checkbox input[type="checkbox"]').prop('checked', checked);
        });
    });
    
    $('body').on('click', 'div.dialog button.close', function() {
        var dialog = $(this).parents('div.dialog:first');
        dialog.dialog('close');
    });

});
