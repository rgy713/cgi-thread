var up_add_field;
var increase_upload_num_checkbox;
var up_add_files;

var set_up_add_field_state = function () {
    var checked = increase_upload_num_checkbox.prop('checked');
    up_add_files.prop('disabled', !checked);
    if (checked) {
        up_add_field.show();
    } else {
        up_add_field.hide();
    }
};

$(function () {
    up_add_field = $("#up_add_field");
    if (up_add_field.length === 0) {
        up_add_field = void 0;
        return;
    }
    increase_upload_num_checkbox = $("#increase_upload_num_checkbox");
    up_add_files = $(".up_add_files");

    set_up_add_field_state();
    increase_upload_num_checkbox.change(set_up_add_field_state);
});
