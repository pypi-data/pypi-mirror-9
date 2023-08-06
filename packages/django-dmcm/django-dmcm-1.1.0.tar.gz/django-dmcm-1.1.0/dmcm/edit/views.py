from __future__ import absolute_import

from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import CreateView, UpdateView

from braces.views import LoginRequiredMixin

from ..models import Page
from ..edit.forms import PageForm


class LogoutUrlMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        if 'logout_url' not in kwargs:
            kwargs['logout_url'] = settings.LOGOUT_URL
        return super(LogoutUrlMixin, self).get_context_data(**kwargs)


class PageListView(LoginRequiredMixin, LogoutUrlMixin, ListView):
    template_name = 'dmcm/edit/page_list.html'
    model = Page


class PageCreateView(LoginRequiredMixin, LogoutUrlMixin, CreateView):
    template_name = 'dmcm/edit/page_detail.html'
    model = Page
    form_class = PageForm

    def get_success_url(self):
        return reverse('dmcm:page_detail', args=(self.object.slug,))


class PageUpdateView(LoginRequiredMixin, LogoutUrlMixin, UpdateView):
    template_name = 'dmcm/edit/page_detail.html'
    model = Page
    form_class = PageForm

    def get_success_url(self):
        return reverse('dmcm:page_detail', args=(self.object.slug,))
