from .template import TemplateRenderer

class Renderer(TemplateRenderer):
    '''Directly pass the config object to the template'''

    def render(self, context):
        context.update(self.config)
        return context
