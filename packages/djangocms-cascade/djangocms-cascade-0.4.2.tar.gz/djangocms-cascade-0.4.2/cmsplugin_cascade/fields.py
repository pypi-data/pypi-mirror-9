# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.forms.util import ErrorList
from django.core.exceptions import ValidationError


class PartialFormField(object):
    """
    Behave similar to django.forms.Field, encapsulating a partial dictionary, stored as
    JSONField in the database.
    """
    def __init__(self, name, widget, label=None, initial='', help_text='', error_class=ErrorList):
        if not name:
            raise AttributeError('The field must have a name')
        self.name = name
        if not isinstance(widget, widgets.Widget):
            raise AttributeError('The field `widget` must be derived from django.forms.widgets.Widget')
        self.label = label or name
        self.widget = widget
        self.initial = initial
        self.help_text = help_text
        self.error_class = error_class

    def run_validators(self, value):
        if not callable(getattr(self.widget, 'validate', None)):
            return
        errors = []
        if callable(getattr(self.widget, '__iter__', None)):
            for field_name in self.widget:
                try:
                    self.widget.validate(value.get(self.name), field_name)
                except ValidationError as e:
                    if isinstance(getattr(e, 'params', None), dict):
                        e.params.update(label=self.label)
                    messages = self.error_class([m for m in e.messages])
                    errors.extend(messages)
        else:
            try:
                self.widget.validate(value.get(self.name))
            except ValidationError as e:
                if isinstance(getattr(e, 'params', None), dict):
                    e.params.update(label=self.label)
                errors = self.error_class([m for m in e.messages])
        if errors:
            raise ValidationError(errors)

    def get_element_ids(self, prefix_id):
        """
        Returns a single or a list of element ids, one for each input widget of this field
        """
        if isinstance(self.widget, widgets.MultiWidget):
            ids = ['{0}_{1}_{2}'.format(prefix_id, self.name, field_name) for field_name in self.widget]
        elif isinstance(self.widget, (widgets.SelectMultiple, widgets.RadioSelect)):
            ids = ['{0}_{1}_{2}'.format(prefix_id, self.name, k) for k in range(len(self.widget.choices))]
        else:
            ids = ['{0}_{1}'.format(prefix_id, self.name)]
        return ids
