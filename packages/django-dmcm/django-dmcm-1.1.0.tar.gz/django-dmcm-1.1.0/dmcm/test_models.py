"""DMCM Models Unit Test."""
from __future__ import absolute_import

from django.conf import settings
from django.test import TestCase

from .factories import PageFactory
from .models import Page


class PageTest(TestCase):
    """
    Create and access Page.
    """
    def setUp(self):
        root_page = PageFactory.create()
        root_page.slug = settings.SITE_ROOT_SLUG
        root_page.content = '{0:s}\nTest Root Page'.format(root_page)
        root_page.parent = root_page
        root_page.save()

        page = PageFactory.create()
        page.title = 'Test'
        page.slug = 'test'
        page.content = '# Test Content'
        page.parent = root_page
        page.save()

        sub_page = PageFactory.create()
        sub_page.title = 'Test 2'
        sub_page.slug = 'test-2'
        sub_page.content = '# Test Content Two'
        sub_page.parent = page
        sub_page.save()

    def test_get_page(self):
        """Retrieve Page objects. Check their attributes."""
        pages = Page.objects.filter(slug='test')
        self.assertEqual(len(pages),
                         1,
                         'Wrong number of pages found: Got %s expected 1' % (len(pages)))
        page = pages[0]
        self.assertEqual(page.title,
                         'Test',
                         'Page: Unexpected title, got %s expected %s' % (page.title, 'Test'))
        absolute_url = page.get_absolute_url()
        self.assertEqual(absolute_url,
                         '/test/',
                         'Unexpected absolute url: Got %s expected "/test/"' % (absolute_url))

        sub_page = Page.objects.get(slug='test-2')
        navigation_path = sub_page.navigation_path()
        self.assertEqual(len(navigation_path),
                         2,
                         'Unexpected navigation path length: Got %s expected 2' % (len(navigation_path)))
        address = navigation_path[1]['address']
        self.assertEqual(address,
                         '/test/',
                         'Unexpected navigation path address: Got %s expected "/test/"' % (address))
