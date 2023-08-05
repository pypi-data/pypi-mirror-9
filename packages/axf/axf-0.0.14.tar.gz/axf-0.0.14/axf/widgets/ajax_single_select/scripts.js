
var AjaxSingleSelectField_init = function(field, other_field, event, datasource, value) {
    var other_field = jQuery(other_field);
    var selected_value = value;

    other_field.change(function() {
        var selected = other_field.val();

        jQuery.getJSON(datasource, {selected: selected}, function(resp){
            var opts = resp.options;

            var options = '';
            for (var i = 0; i < opts.length; i++) {
                if (opts[i].value == selected_value)
                    options += '<option value="' + opts[i].value + '" selected="true">' + opts[i].name + '</option>';
                else
                    options += '<option value="' + opts[i].value + '">' + opts[i].name + '</option>';
            }

            jQuery(field).html(options).change();
        });
    });

    other_field.change();
};