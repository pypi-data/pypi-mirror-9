"""DMCM Edit Forms Unit Test."""

from __future__ import absolute_import

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.views.decorators.csrf import csrf_exempt


class ErrorFormTest(TestCase):
    """Generate Save a ticket via the Admin."""

    @csrf_exempt
    def test_errors_on_form(self):
        """Generate Edit Page showing Errors"""
        self.user = get_user_model().objects.create_user('john',
                                                         'john@montypython.com',
                                                         'password')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client = Client()
        self.client.login(username='john', password='password')

        response = self.client.post('/dmcm/edit/page/add/',
                                    {},
                                    secure=True)

        self.assertEqual(response.status_code,
                         200,
                         'Unexpected status code on add, got %s expected 200' %
                             (response.status_code))

        # Check error message is present in response
        self.assertContains(response,
                            'This field is required.')
