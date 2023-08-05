# -*- coding: utf-8 -*-
"""form base classes for aloha-editor integration"""

import floppyforms as forms

from djaloha.widgets import AlohaInput
from django.utils.encoding import smart_unicode


class DjalohaForm(forms.Form):
    """Base class for form with aloha editor"""

    def __init__(self, model_class, lookup, field_name, data=None, field_value=None, *args, **kwargs):
        super(DjalohaForm, self).__init__(data, *args, **kwargs)
        
        self._model_class = model_class
        self._lookup = lookup
        self._field_name = field_name
        
        model_name = "__".join(
            (model_class.__module__.split('.')[-2], model_class.__name__)
        )
        
        lookup_str = "__".join([k + "__" + unicode(v).strip('"\'') for (k, v) in lookup.items()])
        
        self._form_field = "__".join(
            ("djaloha", model_name, lookup_str, field_name)
        )
        
        self.fields[self._form_field] = forms.CharField(
            required=False,
            initial=field_value,
            widget=AlohaInput()
        )
        
    def save(self):
        """save associated object"""
        value = smart_unicode(self.cleaned_data[self._form_field])
        obj = self._model_class.objects.get_or_create(**self._lookup)[0]
        setattr(obj, self._field_name, value)
        obj.save()
    
    def as_is(self):
        """return html without parent tag"""
        return self._html_output(
            normal_row=u'%(field)s',
            error_row=u'%s',
            row_ender='',
            help_text_html=u'',
            errors_on_separate_row=True
        )
