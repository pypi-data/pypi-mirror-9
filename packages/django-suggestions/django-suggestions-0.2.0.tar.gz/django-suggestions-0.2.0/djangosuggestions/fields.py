from django import forms
from djangosuggestions.widgets import SuggestionWidget


class SuggestionField(forms.CharField):

    widget = SuggestionWidget

    def __init__(self, suggestions=(), *args, **kwargs):
        super(SuggestionField, self).__init__(*args, **kwargs)
        self.suggestions = suggestions

    def _get_suggestions(self):
        return self._suggestions

    def _set_suggestions(self, suggestions):
        self._suggestions = suggestions
        self.widget.suggestions = suggestions

    suggestions = property(_get_suggestions, _set_suggestions)
