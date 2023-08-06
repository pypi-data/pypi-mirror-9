from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

class DocImport(MPTTModel):
    slug = models.SlugField()
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    group = models.CharField(max_length=255)
    html = models.TextField()
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    has_content = models.BooleanField(default=True)

    def __unicode__(self):
        return self.slug

    def save(self, *args, **kwargs):
        self.has_content = len(self.html) > 0
        if self.parent is None:
            self.url = '%s/' % self.slug
        else:
            self.url = ('%s/%s/' % (self.parent.url, self.slug))
            self.url = self.url.replace('//', '/')
            if self.url.startswith('/'):
                self.url = self.url[1:]
        super(DocImport, self).save(*args, **kwargs)
