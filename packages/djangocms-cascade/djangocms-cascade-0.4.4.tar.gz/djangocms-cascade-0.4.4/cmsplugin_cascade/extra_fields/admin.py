# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import re
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.forms import widgets
from django.core.exceptions import ValidationError
from cmsplugin_cascade.fields import PartialFormField
from cmsplugin_cascade.models import PluginExtraFields
from cmsplugin_cascade.widgets import JSONMultiWidget, MultipleCascadingSizeWidget
from cmsplugin_cascade.utils import rectify_partial_form_field
from cmsplugin_cascade.settings import CASCADE_EXTRA_INLINE_STYLES


class ClassNamesWidget(widgets.TextInput):
    """
    Use this field to enter a list of comma separated CSS class names.
    """
    DEFAULT_ATTRS = {'style': 'width: 25em;'}
    validation_pattern = re.compile('^[A-Za-z0-9_-]+$')
    invalid_message = _("In '%(label)s': Value '%(value)s' is not a valid color.")

    def __init__(self, attrs=DEFAULT_ATTRS, required=False):
        self.required = required
        super(ClassNamesWidget, self).__init__(attrs=attrs)

    def validate(self, value):
        for val in value.split(','):
            if val and not self.validation_pattern.match(val.strip()):
                raise ValidationError(_("'%s' is not a valid CSS class name.") % val)


class PluginExtraFieldsAdmin(admin.ModelAdmin):
    list_display = ('plugin_type', 'site')
    DISTANCE_UNITS = (('px,em,%', _("px, em and %")), ('px,em', _("px and em")), ('px', _("px")), ('%', _("%")),)
    classname_fields = ((
        PartialFormField('class_names',
            ClassNamesWidget(),
            label=_("CSS class names"),
            help_text=_("Freely selectable CSS classnames for this Plugin, separated by commas."),
        ),
        PartialFormField('multiple',
            widgets.CheckboxInput(),
            label=_("Allow multiple"),
        ),
    ),)

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css',)}

    def __init__(self, model, admin_site):
        super(PluginExtraFieldsAdmin, self).__init__(model, admin_site)
        self.style_fields = []
        for style, choices_tuples in CASCADE_EXTRA_INLINE_STYLES.items():
            extra_field = PartialFormField('extra_fields:{0}'.format(style),
                widgets.CheckboxSelectMultiple(choices=((c, c) for c in choices_tuples[0])),
                label=_("Customized {0} Fields:").format(style),
            )
            Widget = choices_tuples[1]
            if issubclass(Widget, MultipleCascadingSizeWidget):
                self.style_fields.append((
                    extra_field,
                    PartialFormField('extra_units:{0}'.format(style),
                        widgets.Select(choices=self.DISTANCE_UNITS),
                        label=_("Units for {0} Fields:").format(style),
                        initial=self.DISTANCE_UNITS[0][0],
                    ),
                ))
            else:
                self.style_fields.append(extra_field)

    def get_form(self, request, obj=None, **kwargs):
        """
        Build the form used for changing the model.
        """
        kwargs.update(widgets={'css_classes': JSONMultiWidget(self.classname_fields),
            'inline_styles': JSONMultiWidget(self.style_fields)})
        form = super(PluginExtraFieldsAdmin, self).get_form(request, obj, **kwargs)
        rectify_partial_form_field(form.base_fields['css_classes'], self.classname_fields)
        setattr(form, 'classname_fields', self.classname_fields)
        rectify_partial_form_field(form.base_fields['inline_styles'], self.style_fields)
        setattr(form, 'style_fields', self.style_fields)
        return form

    def has_add_permission(self, request):
        """
        Only if at least one plugin uses the class ExtraFieldsMixin, allow to add an instance.
        """
        return len(PluginExtraFields.CUSTOMIZABLE_PLUGINS) > 0

admin.site.register(PluginExtraFields, PluginExtraFieldsAdmin)
