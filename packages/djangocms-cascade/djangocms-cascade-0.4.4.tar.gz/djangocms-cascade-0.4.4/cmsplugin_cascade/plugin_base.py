# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist
from django.forms.widgets import media_property
from django.utils import six
from django.utils.safestring import SafeText
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBaseMetaclass, CMSPluginBase
from .models_base import CascadeModelBase
from .models import CascadeElement, SharableCascadeElement
from .sharable.forms import SharableGlossaryMixin
from .extra_fields.mixins import ExtraFieldsMixin
from .widgets import JSONMultiWidget
from . import settings


class CascadePluginBaseMetaclass(CMSPluginBaseMetaclass):
    """
    All plugins from djangocms-cascade can be instantiated in different ways. In order to allow this
    by a user defined configuration, this meta-class conditionally inherits from additional mixin
    classes.
    """
    plugins_with_extrafields = list(settings.CASCADE_PLUGINS_WITH_EXTRAFIELDS)
    plugins_with_sharables = dict(settings.CASCADE_PLUGINS_WITH_SHARABLES)

    def __new__(cls, name, bases, attrs):
        if name in cls.plugins_with_extrafields:
            ExtraFieldsMixin.media = media_property(ExtraFieldsMixin)
            bases = (ExtraFieldsMixin,) + bases
        if name in cls.plugins_with_sharables:
            SharableGlossaryMixin.media = media_property(SharableGlossaryMixin)
            bases = (SharableGlossaryMixin,) + bases
            attrs['fields'] += (('save_shared_glossary', 'save_as_identifier'), 'shared_glossary',)
            attrs['sharable_fields'] = cls.plugins_with_sharables[name]
            base_model = SharableCascadeElement
        else:
            base_model = CascadeElement
        model_mixins = attrs.pop('model_mixins', ())
        attrs['model'] = CascadePluginBaseMetaclass.create_model(name, model_mixins, base_model)
        return super(CascadePluginBaseMetaclass, cls).__new__(cls, name, bases, attrs)

    @staticmethod
    def create_model(name, model_mixins, base_model):
        """
        Create a Django Proxy Model on the fly, to be used by any Cascade Plugin.
        """
        class Meta:
            proxy = True

        name += str('Model')
        bases = model_mixins + (base_model,)
        attrs = {'Meta': Meta, '__module__': getattr(base_model, '__module__')}
        model = type(name, bases, attrs)
        return model


class CascadePluginBase(six.with_metaclass(CascadePluginBaseMetaclass, CMSPluginBase)):
    tag_type = 'div'
    change_form_template = 'cascade/admin/change_form.html'
    render_template = 'cms/plugins/generic.html'
    glossary_variables = []  # entries in glossary not handled by a form editor
    model_mixins = ()  # model mixins added to the final Django model

    class Media:
        css = {'all': ('cascade/css/admin/partialfields.css', 'cascade/css/admin/editplugin.css',)}

    def _child_classes(self):
        """All registered plugins shall be allowed as children for this plugin"""
        if getattr(self, '_cached_child_classes', None) is not None:
            return self._cached_child_classes
        self._cached_child_classes = list(getattr(self, 'generic_child_classes', [])) or []
        for p in plugin_pool.get_all_plugins():
            if (isinstance(p.parent_classes, (list, tuple))
              and self.__class__.__name__ in p.parent_classes
              and p.__name__ not in self._cached_child_classes):
                self._cached_child_classes.append(p.__name__)
        return self._cached_child_classes
    child_classes = property(_child_classes)

    def __init__(self, model=None, admin_site=None, glossary_fields=None):
        super(CascadePluginBase, self).__init__(model, admin_site)
        if isinstance(glossary_fields, (list, tuple)):
            self.glossary_fields = list(glossary_fields)
        elif not hasattr(self, 'glossary_fields'):
            self.glossary_fields = []

    @classmethod
    def get_identifier(cls, model):
        """
        Hook to return a description for the current model.
        """
        return SafeText()

    @classmethod
    def get_css_classes(cls, obj):
        """
        Returns a list of CSS classes to be added as class="..." to the current HTML tag.
        """
        css_classes = []
        if hasattr(cls, 'default_css_class'):
            css_classes.append(cls.default_css_class)
        for attr in getattr(cls, 'default_css_attributes', []):
            css_class = obj.glossary.get(attr)
            if isinstance(css_class, six.string_types):
                css_classes.append(css_class)
            elif isinstance(css_class, list):
                css_classes.extend(css_class)
        return css_classes

    @classmethod
    def get_inline_styles(cls, obj):
        """
        Returns a dictionary of CSS attributes to be added as style="..." to the current HTML tag.
        """
        inline_styles = getattr(cls, 'default_inline_styles', {})
        css_style = obj.glossary.get('inline_styles')
        if css_style:
            inline_styles.update(css_style)
        return inline_styles

    @classmethod
    def get_html_tag_attributes(cls, obj):
        """
        Returns a dictionary of attributes, which shall be added to the current HTML tag.
        This method normally is called by the models's property method ``html_tag_ attributes``,
        which enriches the HTML tag with those attributes converted to a list as
        ``attr1="val1" attr2="val2" ...``.
        """
        attributes = getattr(cls, 'html_tag_attributes', {})
        return dict((attr, obj.glossary.get(key, '')) for key, attr in attributes.items())

    @classmethod
    def sanitize_model(cls, obj):
        """
        This method is called, before the model is written to the database. It can be overloaded
        to sanitize the current models, in case a parent model changed in a way, which might
        affect this plugin.
        This method shall return `True`, in case a model change was necessary, otherwise it shall
        return `False` to prevent a useless database update.
        """
        if obj.glossary is None:
            obj.glossary = {}
        return False

    def extend_children(self, parent, wanted_children, child_class, child_glossary=None):
        """
        Extend the number of children so that the parent object contains wanted children.
        No child will be removed if wanted_children is smaller than the current number of children.
        """
        from cms.api import add_plugin
        current_children = parent.get_children().count()
        for _ in range(current_children, wanted_children):
            child = add_plugin(parent.placeholder, child_class, parent.language, target=parent)
            if isinstance(child_glossary, dict):
                child.glossary.update(child_glossary)
            child.save()

    def get_form(self, request, obj=None, **kwargs):
        """
        Build the form used for changing the model.
        """
        glossary_fields = kwargs.pop('glossary_fields', self.glossary_fields)
        kwargs.update(widgets={'glossary': JSONMultiWidget(glossary_fields)}, labels={'glossary': ''})
        form = super(CascadePluginBase, self).get_form(request, obj, **kwargs)
        # help_text can not be cleared using an empty string in modelform_factory
        form.base_fields['glossary'].help_text = ''
        for field in glossary_fields:
            form.base_fields['glossary'].validators.append(field.run_validators)
        setattr(form, 'glossary_fields', glossary_fields)
        return form

    def save_model(self, request, new_obj, form, change):
        if change and self.glossary_variables:
            old_obj = super(CascadePluginBase, self).get_object(request, form.instance.id)
            for key in self.glossary_variables:
                if key not in new_obj.glossary and key in old_obj.glossary:
                    # transfer listed glossary variable from the old to new object
                    new_obj.glossary[key] = old_obj.glossary[key]
        super(CascadePluginBase, self).save_model(request, new_obj, form, change)

    def get_parent_instance(self):
        """
        Get the parent model instance corresponding to this plugin. Returns None if the current
        plugin instance is the root model.
        """
        for model in CascadeModelBase._get_cascade_elements():
            try:
                return model.objects.get(id=self.parent.id)
            except ObjectDoesNotExist:
                pass

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        bases = self.get_ring_bases()
        context['base_plugins'] = ['django.cascade.{0}'.format(b) for b in bases]
        try:
            fields = list(context['adminform'].form.fields)
            fields.remove('glossary')
            context['empty_form'] = len(fields) + len(context['adminform'].form.glossary_fields) == 0
        except KeyError:
            pass
        return super(CascadePluginBase, self).render_change_form(request, context, add, change, form_url, obj)

    def get_ring_bases(self):
        """
        Hook to return a list of base plugins required to build the JavaScript counterpart for the
        current plugin. The named JavaScript plugin must have been created using ``ring.create``.
        """
        return []
