from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from . import utils

if 'cms' in settings.INSTALLED_APPS:

    from cms.models import CMSPlugin

    class PluginRenderer(CMSPlugin):
        __renderer = None

        name = models.CharField(verbose_name=_('name'),
                choices=utils.renderers_choices(),
                max_length=256)

        def get_renderer(self):
            if self.__renderer is None:
                self.__renderer = utils.resolve_renderer(self.name)
            return self.__renderer

        def __unicode__(self):
            return utils.renderer_description(self.get_renderer()) or self.name

