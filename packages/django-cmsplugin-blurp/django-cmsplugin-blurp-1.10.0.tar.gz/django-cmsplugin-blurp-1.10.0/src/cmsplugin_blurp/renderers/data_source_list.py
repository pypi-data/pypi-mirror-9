import logging
log = logging.getLogger(__name__)

from . import data_source


class Renderer(data_source.Renderer):
    """
    Aggregates all data from the sources into a list and expose them to the
    template with the name of its slug
    """
    def render(self, context):
        context[self.slug] = []
        for slug, data in self.get_sources(context):
            try:
                context[self.slug].extend(data.content)
            except Exception as e:
                log.exception("exception occured while extending the list: %s", e)
        return super(Renderer, self).render(context)
