from __future__ import absolute_import

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.views.generic import DetailView, ListView, TemplateView

from .forms import StringSearchForm
from .models import Page


class PageListView(ListView):
    model = Page


class PageDetailView(DetailView):
    model = Page


class RootPageDetailView(PageDetailView):
    def get_object(self, queryset=None):
        return Page.root.get_or_create_root_page()


class Search(TemplateView):
    """
    Simple string search.

    Display entries with titles and/or content which 
    contain the string searched for.
    """
    template_name = 'dmcm/search_results.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = StringSearchForm(request.GET)
        search_string = form.cleaned_data['search_string'] if form.is_valid() else ''
        context['search_string'] = search_string
        if len(search_string) < 3:
            context['too_small'] = True
        else:
            title_matches = Page.objects.filter(title__icontains=search_string)
            content_match_pages = Page.objects.filter(content__icontains=search_string)
            content_matches = []
            search_string_lower = search_string.lower()
            for page in content_match_pages:
                content_lower = page.content.lower()
                number_found = content_lower.count(search_string_lower)
                # Display each line containing matches only once.
                matching_lines = []
                match_pos = content_lower.find(search_string_lower)
                while match_pos >= 0:
                    prev_newline = content_lower.rfind('\n', 0, match_pos)
                    next_newline = content_lower.find('\n', match_pos)
                    if prev_newline > 0 and next_newline > 0:
                        matching_line = page.content[prev_newline:next_newline]
                    elif prev_newline < 0 and next_newline > 0:
                        matching_line = page.content[0:next_newline]
                    elif prev_newline > 0 and next_newline < 0:
                        matching_line = page.content[prev_newline:]
                    else:
                        matching_line = page.content
                    matching_lines.append(matching_line)
                    match_pos = content_lower.find(search_string_lower, next_newline) if next_newline > 0 else -1
                content_matches.append({'page': page,
                                        'matching_lines': matching_lines,
                                        'number_found': number_found})
            context['title_matches'] = title_matches
            context['content_matches'] = content_matches
        return self.render_to_response(context)
