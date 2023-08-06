import abc

from django.core.exceptions import ImproperlyConfigured

class BaseRenderer(object):
    '''A renderer receive a configuration and provider a render
       method which produce the content to render
    '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, slug, config):
        self.slug = slug
        self.config = config
        self.check(config)

    @classmethod
    def check(cls, config):
        errors = cls.check_config(config)
        if errors is None:
            return
        errors = list(errors)
        if errors:
            raise ImproperlyConfigured('{0} configuration errors: {1} {2!r}'.format(
                cls.__name__,
                ', '.join(list(errors)),
                config))

    @classmethod
    def check_config(cls, config):
        if not 'name' in config:
            yield 'name key is missing'

    @abc.abstractmethod
    def render(self, context):
        '''Return the context to render the template'''
        pass

    @abc.abstractmethod
    def render_template(self):
        '''Return a template path or a Template object'''
        pass
