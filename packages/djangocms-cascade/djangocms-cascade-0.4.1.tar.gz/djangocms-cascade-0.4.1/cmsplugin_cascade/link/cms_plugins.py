# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.forms import widgets
from django.utils.translation import ugettext_lazy as _
from cms.plugin_pool import plugin_pool
from cmsplugin_cascade.fields import PartialFormField
from .plugin_base import LinkPluginBase, LinkElementMixin
from .forms import TextLinkForm


class TextLinkPlugin(LinkPluginBase):
    name = _("Link")
    form = TextLinkForm
    model_mixins = (LinkElementMixin,)
    render_template = 'cascade/plugins/link.html'
    text_enabled = True
    allow_children = False
    parent_classes = None
    require_parent = False
    glossary_fields = (
        PartialFormField('title',
            widgets.TextInput(),
            label=_("Title"),
            help_text=_("Link's Title")
        ),
    ) + LinkPluginBase.glossary_fields
    html_tag_attributes = dict(title='title', **LinkPluginBase.html_tag_attributes)
    fields = ('link_content', ('link_type', 'cms_page', 'ext_url', 'mail_to'), 'glossary',)

plugin_pool.register_plugin(TextLinkPlugin)
