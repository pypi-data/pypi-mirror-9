"""Models used to store web pages."""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe
from django.utils.text import slugify

import markdown

MARKDOWN_EXTENSIONS = ['extra', 'tables', 'toc']


class RootPageManager(models.Manager):
    def get_or_create_root_page(self):
        try:
            root_page = Page.objects.get(slug=settings.SITE_ROOT_SLUG)
        except Page.DoesNotExist:
            root_page = Page.objects.create(title='Root',
                                           slug=settings.SITE_ROOT_SLUG,
                                           content='Default Root Page')
            root_page.parent= root_page
            root_page.save()
        return root_page


class Page(models.Model):
    """Page information.

    :Fields:

        title : char
            Title of page.
        slug : slug
            Slugified version of Title.
        parent : foreign_key on page
            Parent page in site structure.
        published : date
            When page was published (usually on the blog).
        updated : date_time
            When page was last updated.
        content : text
            Page content in markdown format.
    """
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, unique=True)
    parent = models.ForeignKey('self',null=True)
    published = models.DateField(null=True, blank=True)
    updated = models.DateTimeField(verbose_name='Time Updated', auto_now=True)
    content = models.TextField(verbose_name='Page body',
                               help_text='Use Markdown syntax.')

    objects = models.Manager()
    root = RootPageManager()

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return self.title

    def content_as_html(self):
        """
        Runs Markdown over a given value, using various
        extensions python-markdown supports.
        """
        return mark_safe(markdown.markdown(force_text(self.content),
                                           MARKDOWN_EXTENSIONS,
                                           safe_mode=False))

    def get_absolute_url(self):
        return reverse('dmcm:page_detail', kwargs={'slug': self.slug})

    def navigation_path(self):
        path = []
        parent = self.parent
        if parent != self:
            while parent != parent.parent:
                path.insert(0, {'title': parent.title,
                                'address': '/' + parent.slug + '/'})
                parent = parent.parent
            path.insert(0, {'title': parent.title, 'address':  reverse('dmcm:root')})
        return path

    def save(self, *args, **kwargs):
        self.slug = slugify(unicode(self.slug))
        super(Page, self).save(*args, **kwargs)