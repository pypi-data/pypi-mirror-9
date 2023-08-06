"""DMCM Unit Test."""
from __future__ import absolute_import

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth import get_user_model

from .factories import PageFactory

TEST_URLS = [
    # (url, status_code, text_on_page)
    ('/', 200, 'Test Root Page'),
    ('/site_map/', 200, 'Site Map'),
    ('/test/', 200, 'Test Page'),
    ('/search/?search_string=test', 200, 'Search Results'),
    ('/search/?search_string=pp', 200, 'too small'),
    ('/dmcm/edit/{0:s}/'.format(settings.SITE_ROOT_SLUG), 200, ''),
]


class WorkingURLsTest(TestCase):
    """
    Visit various URLs on the site to ensure they are working.
    """
    def setUp(self):
        """Create test data and Login Test Client"""
        root_page = PageFactory.create()
        root_page.slug = settings.SITE_ROOT_SLUG
        root_page.content = '{0:s}\nTest Root Page'.format(root_page)
        root_page.parent = root_page
        root_page.save()
        test_page = PageFactory.create()
        test_page.slug = 'test'
        test_page.content = '{0:s}\nTest Page'.format(root_page)
        test_page.parent = root_page
        test_page.save()

        self.user = get_user_model().objects.create_user('john', 'john@montypython.com', 'password')
        self.user.is_staff = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')

    def test_urls(self):
        """Visit each URL in turn"""
        for url, status_code, expected_text in TEST_URLS:
            response = self.client.get(url, secure=True)
            self.assertEqual(response.status_code,
                             status_code,
                             'URL %s: Unexpected status code, got %s expected %s' %
                                (url, response.status_code, status_code))
            if response.status_code == 200:
                self.assertContains(response,
                                    expected_text,
                                    msg_prefix='URL %s' % (url))

