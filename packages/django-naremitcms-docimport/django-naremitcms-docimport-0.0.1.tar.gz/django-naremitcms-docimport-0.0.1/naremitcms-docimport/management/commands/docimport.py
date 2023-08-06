import os
from operator import itemgetter
from importlib import import_module

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from naremitcms.models import Application
from naremitcms-docimport.models import DocImport

class Command(BaseCommand):
    def handle(self, *args, **options):
        # create dummy naremit object
        naremit = {
            'lang': { 'code': 'en', 'is_active': settings.USE_I18N },
            'meta': { 'path': '' },
            'page': { 'cached_url': '' },
            'plugins': {}
        }

        # find all docimport apps
        for app in Application.objects.filter(is_active=True):
            module, function = app.function.rsplit('.', 1)
            module = import_module(module)
            function = getattr(module, function)
            for base in function.__bases__:
                if base.__name__ == 'DocImportApplication':
                    app = function(naremit, None, None, None)
                    self.do_import(app.get_group(), app.get_data_dir(), \
                        app.MARKUP_LANGUAGE)

        # clear the cache
        cache.clear()

    def do_import(self, group, datadir, markup_language):
        # delete previous entries for this group
        DocImport.objects.filter(group=group).delete()

        # create dummy root node
        root = DocImport(slug='', title='', group=group, html='')
        root.save()

        # get files
        files = []
        filelist = [ f for f in os.listdir(datadir) ]
        for f in filelist:
            if os.path.isfile(os.path.join(datadir, f)):
                fprefix = os.path.splitext(f)[0]
                fsplit = fprefix.split(' - ')
                if len(fsplit) == 2:
                    numbers = fsplit[0].split('.')
                    files.append({
                        'number': int(numbers.pop()),
                        'parent': '.'.join(numbers),
                        'slug': slugify(fsplit[1].strip()),
                        'title': fsplit[1].strip(),
                        'filename': os.path.join(datadir, f),
                    })

        # sort list
        files = sorted(files, key=itemgetter('parent', 'number'))

        # loop through nodes
        for f in files:
            if f['parent'] == '':
                doc = DocImport(
                    slug=f['slug'],
                    title=f['title'],
                    group=group,
                    html=self.get_html(f['filename'], markup_language),
                    parent=root
                )
                doc.save()
                self.recurse(files, doc, str(f['number']), group, \
                    markup_language)

    def get_html(self, filename, markup_language):
        f = open(filename, 'r')

        # markdown
        if markup_language == 'markdown':
            from markdown import markdown
            return markdown(f.read())

        # reStructured text
        if markup_language == 'rest':
            from docutils.core import publish_parts
            return publish_parts(f.read(), writer_name='html')['html_body']

    def recurse(self, files, parent_node, parent_string, group, markup_language):
        for f in files:
            if f['parent'] == parent_string:
                doc = DocImport(
                    slug=f['slug'],
                    title=f['title'],
                    group=group,
                    html=self.get_html(f['filename'], markup_language),
                    parent=parent_node
                )
                doc.save()
                self.recurse(files, doc, \
                    '%s.%s' % (parent_string, f['number']), group, \
                    markup_language)
