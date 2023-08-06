from django.utils.translation import ugettext_lazy as _

from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from . import models

class BlurpPlugin(CMSPluginBase):
    name = _('Blurp Plugin')
    text_enabled = True
    model = models.PluginRenderer
    render_template = ''

    def render(self, context, instance, placeholder):
        renderer = instance.get_renderer()
        request = context.get('request')
        ajax = context.get('ajaxy', True) and renderer.config.get('ajax', False)
        if not ajax:
            self.render_template = renderer.render_template()
            return renderer.render(context)
        else:
            request = context.get('request')
            context['plugin_id'] = instance.id
            context['ajax_refresh'] = renderer.config.get('ajax_refresh', 0)
            if request.GET:
                context['plugin_args'] = '?{0}'.format(request.GET.urlencode())
            # hack alert !!
            self.render_template = 'cmsplugin_blurp/ajax.html'
            return context







plugin_pool.register_plugin(BlurpPlugin)
