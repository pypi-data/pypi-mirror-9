from django.forms import Media
from django.core.urlresolvers import reverse
from djinn_core.utils import urn_to_object
from base import InOutWidget


class RelateWidget(InOutWidget):

    """
    Widget for handling relations to other content. The following
    extra attributes are supported:

     * content_type Allowed content types for this relation as list
     * searchfield Look for this field in the searchengine
     * ct_searchfield Use this field to check on the contenttype. Defaults
       to meta_ct.
     * search_minlength Start autosearch when length is this or more
     * search_url Use this URL as search base. Defaults to reverse of
       'djinn_forms_relatesearch'
    *  template_name path to the rendering template. Defaults to
       djinn_forms/snippets/relatewidget.html. Another valid option is
       to use a popup for searcing content. Use
       djinn_forms/snippets/relatesearchwidget.html to do that.

    To actually save the data that this widget produces, you need to
    make your form extend the djinn_forms.forms.RelateMixin and call
    the methods in that form as documented there.

    TODO: add unique setting to make sure the related object is not already in
    """

    initial = False

    def _media(self):

        """ Add JS for TinyMCE """

        return Media(
            js=('js/djinn_forms_relate.js', )
        )

    media = property(_media)

    @property
    def template_name(self):
        return self.attrs.get('template_name',
                              'djinn_forms/snippets/relatewidget.html')

    def convert_item(self, item):

        return urn_to_object(item)

    def build_attrs(self, extra_attrs=None, **kwargs):

        final_attrs = super(RelateWidget, self).build_attrs(
            extra_attrs=extra_attrs, **kwargs)

        url = self.attrs.get("search_url", reverse("djinn_forms_relatesearch"))
        url = "%s?content_type=%s&searchfield=%s&ct_searchfield=%s" % (
            url,
            ",".join(self.attrs['content_type']),
            self.attrs.get("searchfield", "title_auto"),
            self.attrs.get("ct_searchfield", "meta_ct"),
            )

        final_attrs.update(
            {'search_minlength': self.attrs.get("search_minlength", 2),
             'search_url': url
             })

        final_attrs['initial'] = self.initial

        return final_attrs


class RelateSingleWidget(RelateWidget):

    """ Relate widget where only one relation is allowed """

    template_name = 'djinn_forms/snippets/relatesinglewidget.html'

    def value_from_datadict(self, data, files, name):

        """ The data may contain a list of objects to remove, and
        objects to add. Both are prefixed by the field name. The
        returned value is a dict with 'rm' and 'add' lists, that list
        the """

        result = super(RelateSingleWidget, self).value_from_datadict(
            data, files, name)

        result = result.get('add', [])

        if len(result):
            return result[0]
        else:
            return None
