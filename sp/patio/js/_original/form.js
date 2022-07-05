$(function() {
    var disabled_submit_buttons;

    $('#postform').submit(function () {
        var submit_buttons = $(this).find('input[type=submit]');
        submit_buttons.prop('disabled', true);
        disabled_submit_buttons = submit_buttons;
    });

    // this event triggered by history.back() on firefox / safari
    // other browser trigger onLoad event
    $(window).on('pageshow', function(event) {
        if (disabled_submit_buttons != undefined && event.originalEvent.persisted) {
            disabled_submit_buttons.prop('disabled', false);
            disabled_submit_buttons = undefined;
        }
    });
});
