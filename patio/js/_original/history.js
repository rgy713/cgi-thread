// onLoad
$(function () {
    var toggle_element = $('#edit_toggle');

    var set_edit_toggle_state = function () {
        if (toggle_element.hasClass('enabled')) {
            toggle_element.text('ï“èWèIóπ');
            $('.edit_elements').show();
        } else {
            toggle_element.text('ï“èWÇ∑ÇÈ');
            $('.edit_elements').hide();
            $('.edit_checkbox').prop('checked', false);
        }
    };

    set_edit_toggle_state();

    if (('history' in window) && window['history'] !== null) {
        var get_params_keys = (function () {
            var get_params_keys = [];
            var raw_getparam_pairs = location.search.substring(1).split('&');
            for(var i = 0; i < raw_getparam_pairs.length; i++) {
                var separator_match_pos = raw_getparam_pairs[i].search(/=/);
                if (separator_match_pos > 0) {
                    get_params_keys.push(raw_getparam_pairs[i].slice(0, separator_match_pos))
                }
            }
            return get_params_keys;
        })();
        if (get_params_keys.length == 1 && get_params_keys[0] == 'edit') {
            history.replaceState(null, document.title, location.pathname);
        }
    }

    $('#edit_all_select').click(function () {
        $('.edit_checkbox').prop('checked', true);
    });

    toggle_element.click(function () {
        toggle_element.toggleClass('enabled');
        set_edit_toggle_state();
        return false;
    }).show();
});
