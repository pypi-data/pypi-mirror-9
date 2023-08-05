# -*- coding: utf-8 -*-

from django.utils.translation import ugettext as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from griffin.cmsplugin.resume import GriffinPluginModel

class GriffinPlugin(CMSPluginBase):
    model = GriffinPluginModel
    name = _("Resume Griffin Plugin")
    render_template = "griffin/plugin.html" 

    def render(self, context, instance, placeholder):
        context.update({'instance':instance})
        return context

plugin_pool.register_plugin(GriffinPlugin) # register the plugin
