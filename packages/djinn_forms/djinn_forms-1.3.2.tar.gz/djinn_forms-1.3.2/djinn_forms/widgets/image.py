from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class ImageWidget(forms.widgets.Widget):

    """ Image upload widget """

    template_name = "djinn_forms/snippets/imagewidget.html"

    def render(self, name, value, attrs=None):

        try:
            value = self.model.objects.get(pk=value)
        except:
            pass

        context = {
            'name': name,
            'widget': self,
            'show_progress': True,
            'multiple': False,
            'value': value
            }

        context.update(self.attrs)

        if value:
            accessor = "get_%s_url" % self.attrs.get('size', 'thumbnail')
            try:
                context['image_url'] = getattr(value, accessor)()
            except:
                pass

        if attrs:
            context.update(attrs)

        return mark_safe(render_to_string(self.template_name, context))
