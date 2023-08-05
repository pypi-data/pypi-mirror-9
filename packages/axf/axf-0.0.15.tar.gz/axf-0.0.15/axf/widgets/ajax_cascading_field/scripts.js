
var AjaxCascadingField_init = function(field, other_field, event, datasource, value) {
    var other_field = jQuery(other_field);
    var selected_value = value;

    other_field.change(function() {
        var selected = other_field.val();

        jQuery.getJSON(datasource, {selected: selected}, function(resp){
            jQuery(field).val(resp.value);
        });
    });

    other_field.change();
};