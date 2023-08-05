
$(function() {

    $('form').submit(function() {
        if (! $('#username').val()) {
            with ($('#username').get(0)) {
                select();
                focus();
            }
            return false;
        }
        if (! $('#password').val()) {
            with ($('#password').get(0)) {
                select();
                focus();
            }
            return false;
        }
        return true;
    });

    $('#username').focus();

});
