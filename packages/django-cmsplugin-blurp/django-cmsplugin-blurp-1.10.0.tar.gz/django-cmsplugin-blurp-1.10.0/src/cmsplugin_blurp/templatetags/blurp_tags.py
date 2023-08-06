import logging
import json

from django import template
from django.conf import settings
from django.utils.html import escape
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe

from classytags.arguments import Argument
from classytags.core import Options, Tag

from .. import utils

register = template.Library()

# originally copied from django-jsonify(https://bitbucket.org/marltu/django-jsonify/)
# released under a three-clause BSD License by Marius Grigaitis
@register.filter
def jsonify(obj):
    if isinstance(obj, QuerySet):
        return mark_safe(serialize('json', obj))
    return mark_safe(json.dumps(obj, cls=DjangoJSONEncoder))

@register.tag
class RenderBlurp(Tag):
    name = 'render_blurp'
    options = Options(
        Argument('name', resolve=False),
    )


    def render_tag(self, context, name):
        renderer = utils.resolve_renderer(name)
        if not renderer:
            return ''
        template = renderer.render_template()
        context = renderer.render(context)
        try:
            if not hasattr(template, 'render'):
                template = template.Template(template)
            return template.render(context)
        except Exception, e:
            logging.getLogger(__name__).exception('error while rendering %s',
                    renderer)
            msg = ''
            if settings.TEMPLATE_DEBUG:
                msg += 'error while rendering %s: %s' % (renderer, e)
                msg = '<pre>%s</pre>' % escape(msg)
            return msg


@register.tag
class BlurpNode(Tag):
    '''Insert content generated from a blurp block and render inside template'''
    name = 'blurp'
    options = Options(
            Argument('name'),
            blocks=[('endblurp', 'nodelist')])

    def render_tag(self, context, name, nodelist):
        context.push()
        utils.insert_blurp_in_context(name, context)
        output = self.nodelist.render(context)
        context.pop()
        return output
