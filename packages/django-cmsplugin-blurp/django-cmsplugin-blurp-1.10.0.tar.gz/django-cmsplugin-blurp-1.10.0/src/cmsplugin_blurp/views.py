import json
import logging

from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404

from cms.models import CMSPlugin

logger = logging.getLogger(__name__)

def ajax_render(request, plugin_id):
    context = RequestContext(request)
    context['ajaxy'] = False
    plugin = get_object_or_404(CMSPlugin, pk=plugin_id)
    rendered = plugin.render_plugin(context)
    # use another template to render accumulated js and css declarations from sekizai
    content = loader.render_to_string('cmsplugin_blurp/sekizai_render.html',
            {'content': rendered}, context)
    return HttpResponse(json.dumps({'content': content}))

