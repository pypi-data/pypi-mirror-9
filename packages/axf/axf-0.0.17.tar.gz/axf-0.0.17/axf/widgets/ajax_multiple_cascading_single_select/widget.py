from axf.axel import AxelWidgetMixin, AxelScript
from tw2 import forms
from tw2.core import Param

class AjaxMultipleCascadingSingleSelectField(forms.SingleSelectField, AxelWidgetMixin):
    datasource = Param('Url that will be called to retrieve the data', request_local=False)
    onevents = Param('A list of id that specifies which elements '
                     'triggers options to be reloaded from the datasource', request_local=False)
    options = []
    axel_styles = []
    axel_scripts = [AxelScript('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
                               load=False),
                    AxelScript('AjaxMultipleCascadingSingleSelectField', 'scripts.js', load=False,
                               callback='AjaxMultipleCascadingSingleSelectField_init'),
                    AxelScript(['jquery', 'AjaxMultipleCascadingSingleSelectField'], load=True)]

    def prepare(self):
        super(AjaxMultipleCascadingSingleSelectField, self).prepare()
        self.axel_prepare(self.onevents[0], self.onevents[1], self.datasource, self.value)
