=========================
About AXF
=========================

AXF is a collection of ToscaWidgets2 widgets with resources loading
based on the `AXEL Loader <https://github.com/amol-/axel>`_ to perform
resources loading so that it is possible to replace resources and load
widgets from ajax requests.

Installing
=========================

axf can be installed from pypi::

    easy_install axf

or::

    pip install axf

should just work for most of the users

Using Widgets
==========================

To start using AXF widgets you must add axel to your pages so that
widgets can load their resources::

    <script src="https://raw.github.com/amol-/axel/master/src/axel.js"></script>

The AXEL loader is used instead of standard ToscaWidgets2 resources
injection to make possible to load the forms where they are used through
``jQuery.load``, as resources loading and injection is performed by
AXEL not response manipulation to append the resources to head or body
is required.

If you want to load and submit forms through ajax requests in TurboGears
consider using `tgext.ajaxforms <https://bitbucket.org/_amol_/tgext.ajaxforms>`_

Replacing resources required by the widgets can be performed using
the AXEL loader. Most widgets will depend on jQuery and will load it
from the jquery cdn, if your website uses jQuery and you want to use
a different version of it you can easily replace it using::

    axel.register('jquery', 'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js');

Just place your register **before** displaying the widget and your version
of the library will be used.

Each widget will list its resources with the name used to register them
in AXEL, so that you can replace them.

AjaxAutoCompleteField
==========================

``axf.widgets.ajax_autocomplete_field.AjaxAutocompleteField`` is field that provides
autocompletion based on select2 backed by a json based api. Each entry has to provide
a *text* which is displayed to the user and an *id* which is submitted with the form.
*text* and *id* can coincide for plain text autocompletion.

The field requires two parameters ``datasource`` and ``inverse_datasource`` are respectively
the api to retrieve list of data available for the text written by the user and to retrieve
the text corresponding to an already selected entry (for example in case of validation error
or editing existing data)

EXAMPLE::

      city    = AjaxAutocompleteField(label=l_('City'), validator=validators.Validator(required=True),
                                      placeholder=l_('Select City'),
                                      datasource=lurl('/ajax/get_cities'),
                                      inverse_datasource=lurl('/ajax/city_from_id'))

resources
~~~~~~~~~~~~~~~~~~

    * jquery - jquery library
    * select2 - select2 library
    * select2-style - select2 stylesheet

datasource api
~~~~~~~~~~~~~~~~~~

The API is required to accept a term to search as input, to return a list of
``{text: "value", id: "id"}`` entries and a marker to indicate if more data is available::

    @expose('json')
    def get_cities(self, term='', **kw):
        return dict(more=False, results=[dict(text=c[1], id=c[0]) for c in cities_dict.items()])

datasource_inverse api
~~~~~~~~~~~~~~~~~~~~~~~~~

The API is required to accept an id as argument in the form ``/apiname/ID`` and return the
``text`` and ``id`` of the corresponding entry::

    @expose('json')
    def city_from_id(self, city_id=None, **kw):
        return dict(text=cities_dict.get(city_id), id=city_id)


AjaxSingleSelectField
==========================

``axf.widgets.ajax_single_select.AjaxSingleSelectField`` is a field that loads its data
from a datasource api whenever another field changes. This can be used to implement cascading
single select fields, where options available depend on another selection.

The field requires two parameters ``datasource`` which is the api to call to request
for the data available on the value of the other field and ``onevent`` which is
a tuple with a selector and a javascript event (currently ignored) which specifies
which field should trigger data update. Whenever the  field specified by the selector changes
the single select field is reloaded asking to the datasource for the data.

EXAMPLE::

    category = forms.SingleSelectField(label=l_('Category'), options=Deferred(get_categories),
                                       validator=validators.Validator(required=True))
    subcategory = AjaxSingleSelectField(label=l_('Sub Category'), onevent=('#category', 'change'), prompt_text=None,
                                        validator=validators.Validator(required=True),
                                        datasource=lurl('/ajax/get_subcategories'))

resources
~~~~~~~~~~~~~~~~~~

    * jquery - jquery library

datasource api
~~~~~~~~~~~~~~~~~~~~~

The API is required to accept the current value of the field linked by ``onevent`` option
and return a list of options for the ``AjaxSingleSelectField`` in the form
``{name: "name", value: "value"}``::

    @expose('json')
    def get_subcategories(self, selected=None, **kw):
        if not selected:
            return dict(options=[])
        return dict(options=[dict(name=c['name'], value=c['id']) for c in subcategories.get(selected, [])])


AjaxCascadingField
==========================

``axf.widgets.ajax_cascading_field.AjaxCascadingField`` is a field that loads its data
from a datasource api whenever another field changes. This can be used to implement input fields,
where value depend on another selection.

The field requires three parameters ``datasource`` which is the api to call to request
for the data available on the value of the other field, ``onevent`` which is
a tuple with a selector and a javascript event (currently ignored) which specifies
which field should trigger data update and ``type`` which is the type of the input.
Whenever the  field specified by the selector changes the input field is
reloaded asking to the datasourcefor the data.

EXAMPLE::

    category = forms.SingleSelectField(label=l_('Category'), options=Deferred(get_categories),
                                       validator=validators.Validator(required=True))
    category_description = AjaxCascadingField(label=l_('Category Description'),
                                              onevent=('#category', 'change'),
                                              prompt_text=None,
                                              validator=validators.Validator(required=True),
                                              datasource=lurl('/ajax/get_category_description'),
                                              type='textarea')

resources
~~~~~~~~~~~~~~~~~~

    * jquery - jquery library

datasource api
~~~~~~~~~~~~~~~~~~~~~

The API is required to accept the current value of the field linked by ``onevent`` option
and return the value for the ``AjaxCascadingField`` in the form
``{value: "value"}``::

    @expose('json')
    def get_category_description(self, selected=None, **kw):
        if not selected:
            return dict(value='')
        return dict(value=category[selected].get('description'))


WysiHtml5TextArea
==========================

``axf.widgets.wysihtml5_text_area.WysiHtml5TextArea`` is a Text Area with wysiwyg editor

WysiHtml5TextArea requires the same parameter of tw2 TextArea, when you render the result
html you must declare CSS rules for alignment::

    .wysiwyg-text-align-right {
      text-align: right;
    }

    .wysiwyg-text-align-center {
      text-align: center;
    }

    .wysiwyg-text-align-left {
      text-align: left;
    }

`WysiHtml5 Documentation <https://github.com/xing/wysihtml5/wiki/Getting-Started>`_


EXAMPLE::

    description = WysiHtml5TextArea(label=l_('Description'), validator=Validator(required=True), rows=8)

resources
~~~~~~~~~~~~~~~~~~

    * jquery - jquery library
    * wysihtml5 - WYSIHTML5 library
    * wysihtml5ParserRules - WYSIHTML5 parser
    * wysihtml5_text_area.css - WYSIHTML5 style
