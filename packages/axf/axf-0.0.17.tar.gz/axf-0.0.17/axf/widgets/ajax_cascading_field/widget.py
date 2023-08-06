from axf.axel import AxelWidgetMixin, AxelScript
from tw2 import forms
from tw2.core import Param

class AjaxCascadingField(forms.InputField, AxelWidgetMixin):
    axel_styles = []
    datasource = Param('Url that will be called to retrieve the data', request_local=False)
    onevent = Param('A tuple (id, event[currently ignored]) that specifies which event of which element' +
                    'triggers options to be reloaded from the datasource', request_local=False)
    axel_scripts = [AxelScript('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
                               load=False),
                    AxelScript('AjaxCascadingField', 'scripts.js', load=False,
                               callback='AjaxCascadingField_init'),
                    AxelScript(['jquery', 'AjaxCascadingField'], load=True)]

    def prepare(self):
        if self.type == 'textarea':
            self.safe_modify('template')
            self.template = "tw2.forms.templates.textarea"
        super(AjaxCascadingField, self).prepare()
        self.axel_prepare(self.onevent[0], self.onevent[1], self.datasource, self.value)