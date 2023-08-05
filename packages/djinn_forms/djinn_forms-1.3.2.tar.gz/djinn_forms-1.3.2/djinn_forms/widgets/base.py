from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class BaseWidget(Widget):

    """ Base widget that renders a template. Fields that use this widget
    should always provide a value as a list! """

    defaults = {}

    def __init__(self, attrs=None):

        _attrs = self.defaults.copy()

        if attrs:
            _attrs.update(attrs)

        super(BaseWidget, self).__init__(attrs=_attrs)

    @property
    def template_name(self):

        raise NotImplementedError

    def render(self, name, value, attrs=None):

        final_attrs = self.build_attrs(attrs, name=name, value=value)

        final_attrs['value'] = self.prepare_value(value) or []

        html = render_to_string(self.template_name, final_attrs)

        return mark_safe(u"".join(html))

    def prepare_value(self, value):

        """ Allow override of value preparation for the widget """

        return value


class InOutWidget(BaseWidget):

    """Widget that handles data with add and remove lists. The incoming
    data should have <name>_add and <name>_rm values, separzated by
    'InOutwidget.separator'. The widget sets the 'add_value' and
    'rm_value' in InOutWidget.value_from_datadict, to keep track of
    data that has not been handled yet, i.e. in case of form
    validation errors.

    """

    separator = ";;"

    def convert_item(self, item):

        """Convert a single incoming value value to the actual value you need
        """

        return item

    def value_from_datadict(self, data, files, name):

        """The data may contain a list of objects to remove, and objects to
        add. Both are prefixed by the field name. The returned value
        is a dict with 'rm' and 'add' lists, that list the items to be
        removed and/or added. Since this is the one place we actually
        have te submitted data, we also set the add_value and rm_value
        attributes on the widget here.

        """

        result = {'rm': [], 'add': []}

        self.attrs['rm_value'] = data.get('%s_rm' % name, '')
        self.attrs['add_value'] = data.get('%s_add' % name, '')

        for item in data.get("%s_rm" % name, "").split(self.separator):

            try:
                obj = self.convert_item(item)
                result['rm'].append(obj)
            except:
                pass

        for item in data.get("%s_add" % name, "").split(self.separator):

            try:
                obj = self.convert_item(item)
                result['add'].append(obj)
            except:
                pass

        return result
