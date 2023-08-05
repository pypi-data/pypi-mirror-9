from django.forms.widgets import Widget
from django.forms import Media
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from djinn_core.utils import urn_to_object, object_to_urn


TPL = 'djinn_forms/snippets/sharewidget.html'


class ShareWidget(Widget):

    """ Widget for handling relations to other content.
    The following extra attributes are supported:
     * content_types Allowed content types for this relation
     * searchfield Search field to use. Default: 'title'
     * search_minlength Start searching when N chars have been typed.
       Default: 2
    """

    def _media(self):

        """ Add relate JS """

        return Media(
            js=('js/djinn_forms_relate.js', )
        )

    media = property(_media)

    def value_from_datadict(self, data, files, name):

        """ The data may contain a list of objects to remove, and
        objects to add. Both are prefixed by the field name. The
        returned value is a dict with 'rm' and 'add' lists, that list
        the """

        result = {'rm': [], 'add': []}

        for item in data.get("%s_rm" % name, "").split(";;"):

            try:
                obj = urn_to_object(item)
            except:
                obj = None

            if obj:
                result['rm'].append(obj)

        for item in data.get("%s_add" % name, "").split(";;"):

            try:
                obj = urn_to_object(item)
            except:
                obj = None

            if obj:
                result['add'].append(obj)

        return result

    def render(self, name, value, attrs=None):

        url = self.attrs.get("search_url", reverse("djinn_forms_relatesearch"))
        url = "%s?content_type=%s&searchfield=%s" % (
            url,
            ",".join(self.attrs['content_type']),
            self.attrs.get("searchfield", "title")
            )

        if value:
            related = [(object_to_urn(obj), unicode(obj)) for obj in
                       value.get('add', [])]

        if value:
            add_value = ";;".join([rel[0] for rel in related])
            value = [{"value": rel[0], "label": rel[1]} for rel in related]

        context = {'name': name,
                   'hint': self.attrs.get("hint", ""),
                   # Translators: djinn_forms relate add button label
                   'add_label': self.attrs.get("add_label", _("Add")),
                   'value': value,
                   'add_value': add_value,
                   'search_minlength': self.attrs.get("search_minlength", 2),
                   'search_url': url
                   }

        html = render_to_string(TPL, context)

        return mark_safe(u"".join(html))
