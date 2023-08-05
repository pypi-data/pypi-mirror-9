function axf_single_select_with_add_on_button_click(button) {
    var button = jQuery(button);
    var container = button.parent();
    var widget = container.find('select');
    var text = container.find('.-single-select-with-add-text');

    button.hide();
    var name = widget.attr('name');
    widget.removeAttr('name');
    widget.remove();

    text.attr('name', name);
    text.show();
}