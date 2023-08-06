from __future__ import absolute_import

from django import forms
from django.forms.utils import ErrorList

from ..models import Page


class TextErrorList(ErrorList):
    """Format list of errors as text with breaks"""
    def as_textlist(self):
        if not self: return u''
        return u'%s' % '<br>'.join([u'%s' % e for e in self])


class BaseModelForm(forms.ModelForm):
    """Base ModelForm using TextErrorList"""
    def __init__(self, *args, **kwargs):
        super(BaseModelForm, self).__init__(*args, **kwargs)
        self.error_class = TextErrorList


class PageForm(BaseModelForm):
    """Form for Page Model"""
    class Meta:
        model = Page
        fields = '__all__'