# -*- coding: utf-8 -*-
"""template tags"""

from django import template
from django.db.models import get_model

from djaloha.forms import DjalohaForm


register = template.Library()


@register.filter
def convert_crlf(value):
    """
    Replace carriage return and line feed character by their javascript value
    Make possible to include title with those characters in the aloha links
    """
    return value.replace('\r', '\\r').replace('\n', '\\n')


@register.filter
def remove_br(value):
    """
    Remove the <br> tag by spaces except at the end
    Used for providing title without this tag
    """
    return value.replace('<br>', ' ').strip()


class DjalohaEditNode(template.Node):
    """template tag node base class for aloha-editor integration"""
    
    def __init__(self, model_class, lookup, field_name, *args, **kwargs):
        super(DjalohaEditNode, self).__init__()
        self._model_class = model_class
        self._lookup_args = lookup
        self._lookup = {}
        self._field_name = field_name
        self._object = None
        self.read_only = args[0] if args else kwargs.get('read_only', False)
        
    def _get_form_class(self):
        """return associated form"""
        return DjalohaForm
    
    def _resolve_arg(self, value, context):
        """return associated form"""
        value = unicode(value)
        new_value = value.strip('"').strip("'")
        if len(value)-2 == len(new_value):
            return new_value
        else:
            try:
                try:
                    var_name, attr = new_value.strip('.')
                except Exception:
                    var_name, attr = new_value, None
                var = template.Variable(var_name).resolve(context)
                if attr:
                    var_value = getattr(var, attr, '')
                else:
                    var_value = var
                return var_value
            except template.VariableDoesNotExist:
                return value
    
    def _resolve_lookup(self, lookup, context):
        """resolve context. keep string values as is"""
        for (key, value) in self._lookup_args.items():
            lookup[key] = self._resolve_arg(value, context)
                    
    def _render_value(self, context, obj_lookup, value):
        """render form or value depending on edit mode"""

        #if edit mode : activate aloha form
        if (not self.read_only) and context.get('djaloha_edit'):
            form_class = self._get_form_class()
            form = form_class(self._model_class, obj_lookup, self._field_name, field_value=value)
            return form.as_is()
        else:
            return value

    def render(self, context):
        """convert to html"""
        self._resolve_lookup(self._lookup, context)
        
        #get or create the object to edit
        self._object = self._model_class.objects.get_or_create(**self._lookup)[0]
        value = getattr(self._object, self._field_name)
        
        return self._render_value(context, self._lookup, value)


class DjalohaMultipleEditNode(DjalohaEditNode):
    """base class when working with multiple objects to edit"""

    def __init__(self, *args, **kwargs):
        super(DjalohaMultipleEditNode, self).__init__(*args, **kwargs)
        self._objects_to_render = None

    def get_objects_to_render_count(self):
        """returns the number of objects"""
        if self._objects_to_render:
            return len(self._objects_to_render)
    
    def _get_objects(self, lookup):
        """returns the objects"""
        return self._model_class.objects.none()
    
    def _get_object_lookup(self, obj):
        """returns the queryset lookup"""
        return {"id": obj.id}
    
    def _pre_object_render(self, obj):
        """called before rendering each object"""
        return ""
    
    def _post_object_render(self, obj):
        """called after rendering each object"""
        return ""
    
    def _object_render(self, idx, obj, context):
        """called for rendering each object"""
        value = getattr(obj, self._field_name)
        object_content = self._pre_object_render(obj)
        object_content += self._render_value(context, self._get_object_lookup(obj), value)
        object_content += self._post_object_render(obj)
        return object_content
    
    def render(self, context):
        """convert all to html"""
        self._resolve_lookup(self._lookup, context)
        content = u""

        queryset = self._get_objects(self._lookup)
        self._objects_to_render = list(queryset)

        for (idx, obj) in enumerate(self._objects_to_render):
            content += self._object_render(idx, obj, context)
        return content


def get_djaloha_edit_args(parser, token):
    """get templatetag args"""
    full_model_name = token.split_contents()[1]
    lookups = token.split_contents()[2].split(';')
    field_name = token.split_contents()[3]

    app_name, model_name = full_model_name.split('.')
    model_class = get_model(app_name, model_name)

    lookup = {}
    for lookup_item in lookups:
        try:
            key, value = lookup_item.split('=')
        except ValueError:
            raise template.TemplateSyntaxError(
                u"djaloha_edit {0} is an invalid lookup. It should be key=value".format(lookup_item)
            )
        lookup[key] = value
    
    if not lookup:
        raise template.TemplateSyntaxError(u"The djaloha_edit templatetag requires at least one lookup")
    return model_class, lookup, field_name
