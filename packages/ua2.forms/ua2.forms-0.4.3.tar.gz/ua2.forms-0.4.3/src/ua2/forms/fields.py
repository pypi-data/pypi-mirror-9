from django.forms import TypedChoiceField, ChoiceField
from django.shortcuts import _get_queryset

from .widgets import SelectCallback


class RelatedChoiceField(TypedChoiceField):
    widget = SelectCallback

    def __init__(self, model, add_empty=False,
                 label_name=None, value_name=None,
                 empty_label=None, empty_value=None,
                 coerce=None, filter=None, **kwargs):
        self.model = model
        self.add_empty = add_empty
        self.label_name = label_name
        self.value_name = value_name
        self.empty_label = empty_label
        self.empty_value = empty_value
        self.coerce = coerce or self.model_coerce
        self.filter = filter
        super(ChoiceField, self).__init__(**kwargs)
        self._choices_data = None
        self._request = None

    def __deepcopy__(self, memo):
        result = super(ChoiceField, self).__deepcopy__(memo)
        result._choices_data = None
        result.widget.choices_callback = result.choices_callback
        return result

    def model_coerce(self, value):
        return _get_queryset(self.model).get(pk=value)

    def choices_callback(self):
        return self.choices

    @property
    def choices(self):
        if self._choices_data is None:
            self._choices_data = self.populate()
        return self._choices_data

    def populate(self):
        choices = []
        if self.add_empty:
            choices.append((self.empty_value or '',
                            self.empty_label or '-------'))


        def _get_field(obj, fieldname=None):
            if fieldname:
                value = getattr(obj, fieldname)
                if callable(value):
                    value = value()
            else:
                value = unicode(obj)
            return value

        qs = _get_queryset(self.model)
        if self.filter:
            if callable(self.filter):
                _data = self.filter(self._request)
            else:
                _data = self.filter
            qs = qs.filter(**_data)

        for item in qs:
            label = _get_field(item, self.label_name)
            value = _get_field(item, self.value_name or 'pk')
            choices.append((unicode(value),
                            label))
        return choices
