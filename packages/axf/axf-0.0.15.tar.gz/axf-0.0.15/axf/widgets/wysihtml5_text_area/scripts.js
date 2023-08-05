var WysiHtml5TextArea_init = function(field) {
    var field_play_id = field.substring(1);
    var editor = new wysihtml5.Editor(field_play_id, { // id of textarea element
        toolbar: jQuery(field).siblings('.wysihtml5-toolbar')[0],
        stylesheets: ["/tw2/resources/axf.widgets.wysihtml5_text_area.widget/resources/wysihtml5_text_area.css"],
        parserRules:  wysihtml5ParserRules
    });
}