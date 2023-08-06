from django import forms


class StringSearchForm(forms.Form):
    """
    Allow user to enter a string to search the site for matching pages.
    """
    search_string = forms.CharField()
