import logging

from sqlalchemy import create_engine
from sqlalchemy.sql import text, bindparam
from sqlalchemy.pool import NullPool

from . import template

log = logging.getLogger(__name__)

class Renderer(template.Renderer):
    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.engine = create_engine(self.config['url'],
                poolclass=NullPool, **self.config.get('kwargs', {}))
        self.views = self.config['views']

    def render(self, context):
        for view in self.views:
            query = view['query']
            bindparams = []
            for name, value in view.get('bindparams', {}).iteritems():
                param = bindparam(name, value=value)
                bindparams.append(param)
            sql = text(query, bindparams=bindparams)
            result = self.engine.execute(sql)
            keys = result.keys()
            result = [dict(zip(keys, row)) for row in result.fetchall()]
            context[view['slug']] = result
        return context

