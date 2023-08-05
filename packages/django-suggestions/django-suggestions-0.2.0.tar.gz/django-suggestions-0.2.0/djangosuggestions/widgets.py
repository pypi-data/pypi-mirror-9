from django.forms.utils import flatatt
from django.forms.widgets import TextInput
from django.utils.html import conditional_escape, format_html, format_html_join
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.safestring import mark_safe
from itertools import chain


class SuggestionWidget(TextInput):

    def __init__(self, suggestions=(), *args, **kwargs):
        super(SuggestionWidget, self).__init__(*args, **kwargs)
        self.suggestions = list(suggestions)

    def render(self, name, value, attrs=None, suggestions=()):
        attrs = attrs or {}
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)

        if has_id:
            list_id = attrs['id'] + '__list'
            options = (format_html('<option>{0}</option>', suggestion)
                       for suggestion in chain(self.suggestions, suggestions))

            attrs['list'] = list_id
            datalist = '<datalist{attrs}><select>{options}</select></datalist>'.format(
                attrs=flatatt({'id': list_id}),
                options=''.join(options))
        else:
            datalist = ''

        out = super(SuggestionWidget, self).render(name, value, attrs)
        return mark_safe(out + datalist)
