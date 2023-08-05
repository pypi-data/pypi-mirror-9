from djangosuggestions import fields
from django.db.models import CharField
from django.utils.translation import ugettext, ugettext_lazy as _


class SuggestionField(CharField):

    description = _("text field with suggestions")
    suggestions = ()

    def __init__(self, suggestions=(), *args, **kwargs):
        self.suggestions = suggestions
        super(SuggestionField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': fields.SuggestionField,
            'suggestions': self.suggestions,
        }
        defaults.update(kwargs)
        return super(SuggestionField, self).formfield(**defaults)

    def south_field_triple(self):
        from south.modelsinspector import introspector
        args, kwargs = introspector(self)
        return ('djangosuggestions.models.SuggestionField', args, kwargs)

