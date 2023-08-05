from djinn_forms.widgets.richtext import RichTextWidget


class RichTextMixin(object):

    """ Rich text mixin that sets the instance to the richttext widget """

    def init_richtext_widgets(self):

        for f_name, field in self.fields.items():
            if isinstance(field.widget, RichTextWidget):
                self.fields[f_name].widget.instance = self.instance
