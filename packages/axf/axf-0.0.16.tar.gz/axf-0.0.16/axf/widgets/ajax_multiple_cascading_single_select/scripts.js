
var AjaxMultipleCascadingSingleSelectField_init = function(field, field1, field2, datasource, value) {
    var Jfield1 = jQuery(field1);
    var Jfield2 = jQuery(field2);
    var selected_value = value;
    Jfield1.change(function() {
        var selected1 = Jfield1.val();
        var selected2 = Jfield2.val();
        console.log('1 sta dnandodd', selected1, selected2, selected_value);
        jQuery.getJSON(datasource, {val1: selected1, val2:selected2}, function(resp){
            var opts = resp.options;
            var options = '';
            for (var i = 0; i < opts.length; i++) {
                console.log(selected_value);

                if (opts[i].value == selected_value){
                    options += '<option value="' + opts[i].value + '" selected="true">' + opts[i].name + '</option>';
                    selected_value = '';
                }
                else
                    options += '<option value="' + opts[i].value + '">' + opts[i].name + '</option>';
            }
            jQuery(field).html(options).change();
        });
    });

    Jfield2.change(function() {
        var selected1 = Jfield1.val();
        var selected2 = Jfield2.val();
        console.log('2 sta dnandodd', selected1, selected2);
        jQuery.getJSON(datasource, {val1: selected1, val2:selected2}, function(resp){
            var opts = resp.options;

            var options = '';
            for (var i = 0; i < opts.length; i++) {
                if (opts[i].value == selected_value){
                    options += '<option value="' + opts[i].value + '" selected="true">' + opts[i].name + '</option>';
                    selected_value = '';}
                else
                    options += '<option value="' + opts[i].value + '">' + opts[i].name + '</option>';
            }
            jQuery(field).html(options).change();
        });
    });

};