import os.path

from django.test import TestCase
from django.test.utils import override_settings

from django.template import Context

from cmsplugin_blurp import utils

BASE_FILE = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    'tests_data'))

CMS_PLUGIN_BLURP_RENDERERS = {
    'static': {
        'template': 'test.html',
        'class': 'cmsplugin_blurp.renderers.static.Renderer',
        'content': 'xxx',
    },
}
for kind in ('raw', 'json', 'rss', 'xml'):
    CMS_PLUGIN_BLURP_RENDERERS[kind] = {
            'template': 'test.html',
            'class': 'cmsplugin_blurp.renderers.data_source.Renderer',
            'sources': [
                {
                    'slug': kind,
                    'parser_type': kind,
                    'url': 'file://' + os.path.join(BASE_FILE, kind),
                }
            ]
        }

CMS_PLUGIN_BLURP_LIST_RENDERERS = {
    'json': {
        'template': 'test.html',
        'class': 'cmsplugin_blurp.renderers.data_source_list.Renderer',
        'sources': [
            {
                'slug': 'list_data_source1',
                'parser_type': 'json',
                'url': 'file://' + os.path.join(BASE_FILE, 'json'),
            },
            {
                'slug': 'list_data_source2',
                'parser_type': 'json',
                'url': 'file://' + os.path.join(BASE_FILE, 'json'),
            }
        ]
    }
}

@override_settings(CMS_PLUGIN_BLURP_RENDERERS=CMS_PLUGIN_BLURP_RENDERERS)
class RendererTestCase(TestCase):
    def test_choices(self):
        self.assertEqual(set(utils.renderers_choices()),
                set([('static', 'static'),
                 ('raw', 'raw'),
                 ('json', 'json'),
                 ('rss', 'rss'),
                 ('xml', 'xml'),
                ]))

    def test_static_renderer(self):
        r = utils.resolve_renderer('static')
        self.assertIsNotNone(r)
        c = r.render(Context())
        self.assertTrue(c.has_key('content'))
        self.assertTrue(c.has_key('template'))
        self.assertEqual(c['content'], 'xxx')

    def test_data_source_renderer_raw(self):
        r = utils.resolve_renderer('raw')
        self.assertIsNotNone(r)
        c = r.render(Context())
        self.assertTrue(c.has_key('raw'))
        self.assertEqual(unicode(c['raw']()), 'xxx')

    def test_data_source_renderer_json(self):
        r = utils.resolve_renderer('json')
        self.assertIsNotNone(r)
        c = r.render(Context())
        self.assertTrue(c.has_key('json'))
        self.assertEqual(c['json'](), {'xxx':'yyy'})

    def test_data_source_renderer_rss(self):
        r = utils.resolve_renderer('rss')
        self.assertIsNotNone(r)
        c = r.render(Context())
        self.assertTrue(c.has_key('rss'))
        self.assertIn('feed', c['rss']())

    def test_data_source_renderer_xml(self):
        r = utils.resolve_renderer('xml')
        self.assertIsNotNone(r)
        c = r.render(Context())
        self.assertTrue(c.has_key('xml'))
        self.assertEqual(c['xml']().tag, 'html')

@override_settings(CMS_PLUGIN_BLURP_RENDERERS=CMS_PLUGIN_BLURP_LIST_RENDERERS)
class DataSourceListRenderTestCase(TestCase):

    def test_data_source_list_render_json(self):
        r = utils.resolve_renderer('json')
        self.assertIsNotNone(r)
        c = r.render(Context())
        self.assertTrue(c.has_key('json'))
        self.assertIsInstance(c['json'], list)
