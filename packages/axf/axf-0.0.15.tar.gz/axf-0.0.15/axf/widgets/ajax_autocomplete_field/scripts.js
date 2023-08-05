
var AjaxAutocompleteField_init = function(field, placeholder, datasource, inverse_datasource, options) {
    var data_adapter = function(term, page) {
        return { term: term, page: page };
    };

    var results_adapter = function(data, page) {
        return { results: data.results };
    };

    var init_selection = function (element, callback) {
        jQuery.post(inverse_datasource, { ids: element.val()},
            function(data) {
            if (data.results)
                callback(data.results);
            else
                callback(data);
        });
    };

    jQuery(field).select2({'placeholder': placeholder,
                           'allowClear': true,
                           'multiple': options['multiple'],
                           'minimumInputLength': 3,
                           'initSelection': init_selection,
                           'ajax': {'url':datasource,
                                    'dataType':'json',
                                    'data':data_adapter,
                                    'results':results_adapter}});
};
