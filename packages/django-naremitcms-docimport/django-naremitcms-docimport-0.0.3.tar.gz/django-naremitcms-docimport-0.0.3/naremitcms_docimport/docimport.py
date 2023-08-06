import os

from django.conf import settings
from django.core.cache import cache

from naremitcms.classes import NaremitApplication
from .models import DocImport

class DocImportApplication(NaremitApplication):
    # define the markup language to use, current options are:
    #  - 'markdown': Markdown (default)
    #  - 'rest': reStructured Text
    # it is trivial to add other markup languages, just add them to the
    # get_html() function in docimport/management/commands/docimport.py
    MARKUP_LANGUAGE = 'markdown'

    # The template used for the documentation pages
    TEMPLATE = 'naremitcms-docimport/example.html'

    def find_current(self, url, tree):
        for node in tree:
            if node['url'] == url:
                self.node_id = node['id']
                break
            else:
                self.find_current(url, node['children'])

    def get_data_dir(self):
        if not os.path.isdir(self.DATA_DIR):
            raise Exception('Invalid DATA_DIR directory')
        return self.DATA_DIR

    def get_group(self):
        return ('%s.%s' % (
            self.__class__.__module__,
            self.__class__.__name__)
        )[-255:]

    def get_tree(self):
        # get from cache
        cache_key = ('%s_docimporttree' % self.get_group())[-230:]
        tree = cache.get(cache_key)
        if tree is not None:
            return tree

        # not in cache, generate tree
        try:
            root = DocImport.objects.get(group=self.get_group(), level=0)
            tree = self.get_tree_recurse(root)
        except:
            tree = []

        # save to cache
        cache.set(cache_key, tree, 60 * 60 * 24)
        return tree

    def get_tree_path(self):
        path = '/%s' % self.naremit['page']['cached_url']
        if self.naremit['lang']['is_active']:
            path = '/%s%s' % (self.naremit['lang']['code'], path)
        return path

    def get_tree_recurse(self, parent_node):
        nodes = parent_node.get_children().values('id', 'url', 'title', 'has_content')
        for node in nodes:
            node['children'] = self.get_tree_recurse(DocImport.objects.get(id=node['id']))
        return nodes

    def homepage(self):
        self.set_context('docimport', {
            'tree': self.get_tree(),
            'path': self.get_tree_path(),
        })

    def page(self, url):
        self.node_id = None
        tree = self.get_tree()
        self.find_current('%s/' % url, tree)

        # output
        if self.node_id is None:
            self.raise_404()
        else:
            self.set_template(self.TEMPLATE)
            self.set_context('docimport', {
                'tree': tree,
                'path': self.get_tree_path(),
                'html': DocImport.objects.get(id=self.node_id).html
            })

    def urls(self):
        return (
            (r'^$', 'homepage'),
            (r'^(?P<url>(.*))$', 'page'),
        )

    # untested
    def sitemap(self):
        urls = []
        path = '/%s' % self.naremit['page']['cached_url']
        tree = DocImport.objects.all()
        for node in tree:
            urls.append( ('%s%s' % (path, node.url)).replace('//', '/') )

        # handle multilanguage
        if self.naremit['lang']['is_active']:
            multilang_urls = []
            for lang in settings.LANGUAGES:
                for url in urls:
                    multilang_urls.append('/%s%s' % (lang[0], url))
            return multilang_urls
        else:
            return urls
