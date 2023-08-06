from tw2 import forms
from tw2.core import Param, Link
from axf.axel import AxelWidgetMixin, AxelScript, AxelStyle

class WysiHtml5TextArea(forms.TextArea, AxelWidgetMixin):
    template = "axf.widgets.wysihtml5_text_area.wysihtml5_text_area"
    axel_styles = [AxelStyle('wysihtml5_text_area', 'resources/wysihtml5_text_area.css')]

    axel_scripts = [AxelScript('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
                               load=False),
                    AxelScript('wysihtml5', 'resources/wysihtml5-0.3.0.min.js', load=False),
                    AxelScript('wysihtml5ParserRules', 'resources/parser_rules/advanced.js', load=False),
                    AxelScript('WysiHtml5TextArea', 'scripts.js', load=False,
                               callback='WysiHtml5TextArea_init'),
                    AxelScript(['jquery', 'wysihtml5', 'wysihtml5ParserRules', 'WysiHtml5TextArea'], load=True)]

    def prepare(self):
        super(WysiHtml5TextArea, self).prepare()
        self.axel_prepare()