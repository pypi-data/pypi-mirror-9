from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from . import app_settings

def renderer_description(renderer):
    if 'name' in renderer.config:
        if 'template_name' in renderer.config:
            return _('{name} using template {template}').format(
                    name=renderer.config['name'],
                    template=renderer.config['template_name'])
        else:
            return renderer.config['name']

def renderers_choices():
    for slug in app_settings.RENDERERS:
        renderer = resolve_renderer(slug)
        yield slug, renderer_description(renderer) or slug

def create_renderer(name, instance):
    '''Create a renderer instance of given name from a settings dictionary'''
    module_name, class_name = instance['class'].rsplit('.', 1)
    module = import_module(module_name)
    return getattr(module, class_name)(name, instance)

def resolve_renderer(name):
    '''Create a renderer instance from slug name of its settings'''
    instance = app_settings.RENDERERS.get(name)
    if instance:
        return create_renderer(name, instance)

def insert_blurp_in_context(name, context):
        renderer = resolve_renderer(name)
        if not renderer:
            return ''
        return renderer.render(context)
