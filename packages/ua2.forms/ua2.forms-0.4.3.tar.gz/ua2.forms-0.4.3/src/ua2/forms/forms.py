from django import forms
from django.db import models
from django.db.models.fields import FieldDoesNotExist

from .base import BaseForm

class RequestModelForm(BaseForm, forms.ModelForm):
    _ref_class = forms.ModelForm


class RequestForm(BaseForm, forms.Form):
    _ref_class = forms.Form

    def set_model_fields(self, instance, exclude_fields=None):
        '''Fills values from the form fields into instance fields'''
        exclude = exclude_fields or []
        data = self.cleaned_data
        for key in data:
            if key in instance._meta.get_all_field_names() and not key in exclude:
                field = instance._meta.get_field(key)
                #FIXME: replace if with follow statement
                # if isinstance(field, (models.ImageField, models.FileField)):
                if type(field) in (models.ImageField, models.FileField):
                    if data[key] != None:
                        if data[key] == False:
                            data[key] = None
                        setattr(instance, key, data[key])
                elif type(field) in (models.ForeignKey,
                                     models.IPAddressField,
                                     models.GenericIPAddressField):
                    if data[key]:
                        setattr(instance, key, data[key])
                    else:
                        setattr(instance, key, None)
                else:
                    setattr(instance, key, data[key])

    def set_initial(self, instance):
        for fieldname in self.fields.keys():
            field = self.fields[fieldname]
            try:
                field_type = type(instance._meta.get_field(fieldname))
            except FieldDoesNotExist:
                continue

            if fieldname in self.initial:
                continue
            if hasattr(instance, fieldname):
                attr = getattr(instance, fieldname)
                if callable(attr):
                    attr = attr()

                if attr is None:
                    continue

                if type(field) == forms.ModelMultipleChoiceField:
                    self.initial[field] = attr.all()
                elif field_type == models.ManyToManyField:
                    self.initial[fieldname] = [t.pk for t in attr.all()]
                elif field_type == models.ForeignKey:
                    self.initial[fieldname] = attr.pk
                else:
                    self.initial[fieldname] = attr
