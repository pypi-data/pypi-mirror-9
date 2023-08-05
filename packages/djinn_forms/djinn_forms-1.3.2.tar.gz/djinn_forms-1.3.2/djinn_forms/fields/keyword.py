import re
from django.forms.fields import Field
from djinn_forms.widgets.keyword import KeywordWidget


class KeywordField(Field):

    """ Field for adding keywords to content """

    widget = KeywordWidget

    def prepare_value(self, data):

        if not data:
            return []

        return re.split("\W+", data)
