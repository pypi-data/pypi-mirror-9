from django.forms import Media
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.forms.util import flatatt


TPL = 'djinn_forms/snippets/richtextwidget.html'


class RichTextWidget(Widget):

    """ Widget that provides wysiwyg capabilities for fields. The following
    attributes are supported:
     * enable_images Defaults to True
     * enable_links Defaults to True
     * maxchars Set counter to widget
    """

    instance = None

    def __init__(self, img_type="djinn_contenttypes.ImgAttachment",
                 enable_images=True, enable_links=True, maxchars=-1,
                 attrs=None):

        super(RichTextWidget, self).__init__(attrs=attrs)

        self.img_type = img_type
        self.maxchars = maxchars
        self.enable_links = enable_links
        self.enable_images = enable_images

    def _media(self):

        """ Add JS for TinyMCE """

        return Media(
            js=('tinymce/tinymce.jquery.js',
                'tinymce/jquery.tinymce.min.js',
                'js/djinn_forms_richtext.js',
                'js/djinn_forms_link.js')
        )

    media = property(_media)

    def render(self, name, value, attrs=None):

        """ Render the widget as HTML """

        if value is None:
            value = ''

        final_attrs = self.build_attrs(attrs, name=name)

        context = {
            'attributes': flatatt(final_attrs),
            'name': name,
            'hint': self.attrs.get("hint", ""),
            'value': force_text(value),
            'enable_images': self.enable_images,
            'enable_links': self.enable_links,
            'maxchars': self.maxchars
        }

        if self.instance:
            context['ctype'] = self.instance.ct_name
            context['cid'] = self.instance.id
            context['img_type'] = self.img_type

        html = render_to_string(TPL, context)

        return mark_safe(u"".join(html))
