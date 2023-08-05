from django import forms
from django.db import models
from django.utils.text import capfirst
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.core.validators import EMPTY_VALUES
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _


class TruncatedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, empty_label="---------", cache_choices=False,
                 truncate_suffix='...', truncate_chars=None,
                 required=True, widget=None, label=None, initial=None,
                 help_text=None, to_field_name=None, *args, **kwargs):

        self.truncate_chars = truncate_chars
        self.truncate_suffix = truncate_suffix

        super(TruncatedModelChoiceField, self).__init__(queryset,
            empty_label=empty_label, cache_choices=cache_choices,
            required=required, widget=widget, label=label, initial=initial,
            help_text=help_text, to_field_name=to_field_name, *args, **kwargs)

    def label_from_instance(self, obj):
        if self.truncate_chars:
            return smart_text(obj)[:self.truncate_chars] +\
                   (smart_text(obj)[self.truncate_chars:] and self.truncate_suffix)
        return smart_text(obj)


class RangeField(forms.Field):
    default_error_messages = {
        'invalid': _("Enter a number or range of numbers with '-' separator."),
    }

    def to_python(self, value):
        """
        Validates input value. It has to be number of range of number.
        Returns the list or range limits or None for empty values.
        """
        if value in EMPTY_VALUES:
            return None
        value = value.strip()
        #value = smart_text(value)

        #if self.localize:
        #    value = formats.sanitize_separators(value)

        try:
            value = float(value)
            start = value
            stop = value
            return start, stop
        except (ValueError, TypeError):
            pass

        try:
            start, stop = value.split('-', 1)
            start = float(start.strip())
            stop = float(stop.strip())
            return start, stop
        except (ValueError, TypeError):
            raise ValidationError(self.error_messages['invalid'])


# New version of this snippet http://djangosnippets.org/snippets/1200/
class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple

    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
            # if value and self.max_choices and len(value) > self.max_choices:
        #     raise forms.ValidationError('You must select a maximum of %s choice%s.'
        #             % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value


class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name),
                    'help_text': self.help_text, 'choices': self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    def get_prep_value(self, value):
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def to_python(self, value):
        if value is not None:
            return value if isinstance(value, list) else value.split(',')
        return ''

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices): ",".join([choicedict.get(value, value) for value in getattr(self, fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)

    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if opt_select not in arr_choices:  # the int() here is for comparing with integer choices
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)
        return

    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


# needed for South compatibility

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^pragmatic\.fields\.MultiSelectField"])


# Example Model

#TYPES = ((1, 'Product'),
#(2, 'Service'),
#(3, 'Skill'),
#(4, 'Partnership')),
#(5, 'Question'),
#)
#
#class Exchange(models.Model):
#    types = MultiSelectField(max_length=250, blank=True, choices=TYPES)
#    ...
#
## Example Form
#
#class ExchangeForm(forms.Form):
#    types = MultiSelectFormField(choices=TYPES)
#    ...
