from django.forms import Media
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from djinn_core.utils import urn_to_object


class LinkWidget(Widget):

    """ Link widget for internal and external links """

    def _media(self):

        """ Add JS for TinyMCE """

        return Media(
            js=('js/djinn_forms_link.js', )
        )

    media = property(_media)

    def render(self, name, value, attrs=None):

        lexval = ""

        if value:
            url = value.split("::")[0]

            if url.startswith("urn"):
                lexval = urn_to_object(url).title
            else:
                lexval = url or ""

        context = {'name': name,
                   'lexical_value': lexval,
                   'value': value or "",
                   }

        html = render_to_string('djinn_forms/snippets/link_widget.html',
                                context)

        return mark_safe(u"".join(html))
