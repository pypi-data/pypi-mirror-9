from clld.tests.util import TestWithApp
from clld import RESOURCES


class Tests(TestWithApp):
    def test_robots(self):
        self.app.get('/robots.txt')

    def test_sitemapindex(self):
        self.app.get_xml('/sitemap.xml')

    def test_sitemap(self):
        self.app.get_xml('/sitemap.language.0.xml')
        self.app.get_json('/resourcemap.json?rsc=language')
        self.app.get_json('/resourcemap.json?rsc=parameter')
        self.app.get_json('/resourcemap.json?rsc=xxx', status=404)

    def test_dataset(self):
        self.app.get_html('/?__admin__=1')
        self.app.get_xml('/', accept='application/rdf+xml')
        self.app.get('/void.md.ris')

    def test_resources(self):
        for rsc in RESOURCES:
            if not rsc.with_index:  # exclude the special case dataset
                continue
            self.app.get_html('/{0}s/{0}'.format(rsc.name))
            self.app.get_html('/{0}s/{0}.snippet.html'.format(rsc.name), docroot='div')
            self.app.get_xml('/{0}s/{0}.rdf'.format(rsc.name))
            self.app.get_html('/%ss' % rsc.name)
            self.app.get_xml('/%ss.rdf' % rsc.name)
            self.app.get_dt('/%ss?iDisplayLength=5' % rsc.name)
        self.app.get_html('/combinations/parameter')

    def test_source(self):
        for ext in 'bib en ris mods'.split():
            self.app.get('/sources/source.' + ext)
            self.app.get('/sources.' + ext)
        self.app.get_xml('/sources.rdf?sEcho=1')

    def test_replacement(self):
        self.app.get('/languages/replaced', status=301)
        self.app.get('/languages/gone', status=410)
        self.app.get('/sources/replaced', status=301)
