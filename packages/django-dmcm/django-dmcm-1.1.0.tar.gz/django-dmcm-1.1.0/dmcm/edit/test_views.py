"""DMCM Edit Views Unit Test."""

from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.views.decorators.csrf import csrf_exempt

from ..factories import PageFactory
from ..models import Page


class PageCreateUpdateTest(TestCase):
    """Create and Update Page."""

#    @csrf_exempt
    def setUp(self):
        """Create test data and Login Test Client"""
        root_page = PageFactory.create()
        root_page.slug = settings.SITE_ROOT_SLUG
        root_page.content = '{0:s}\nTest Root Page'.format(root_page)
        root_page.parent = root_page
        root_page.save()
        self.root_page = root_page

        self.user = get_user_model().objects.create_user('john',
                                                         'john@montypython.com',
                                                         'password')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')

    def test_page_add_view(self):
        """Create a Page using the view"""
        response = self.client.post('/dmcm/edit/page/add/',
                                    {'title': 'Test Page',
                                     'slug': 'test-page',
                                     'parent': self.root_page.pk,
                                     'content': 'Test Content',
                                    },
                                    secure=True)
        self.assertEqual(response.status_code,
                         302,
                         'Unexpected status code on add, got %s expected 302' %
                             (response.status_code))

        test_page = Page.objects.get(slug='test-page')
        self.assertEqual(test_page.title,
                         'Test Page',
                         'Unexpected Page title after add, got "%s" expected "Test Page"' %
                             (response.status_code))

        # Update the test Page
        response = self.client.post('/dmcm/edit/test-page/',
                                    {'title': 'Test Page',
                                     'slug': 'test-page',
                                     'parent': self.root_page.pk,
                                     'content': '# Test Content Updated',
                                    },
                                    secure=True)

        self.assertEqual(response.status_code,
                         302,
                         'Unexpected status code on add, got %s expected 302' %
                             (response.status_code))
