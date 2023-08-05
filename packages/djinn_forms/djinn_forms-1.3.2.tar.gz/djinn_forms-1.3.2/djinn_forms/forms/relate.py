from djinn_forms.fields.relate import RelateField


class RelateMixin(object):

    """ When using relate fields, handle these in the save of your
    form. """

    def save_relations(self, commit=True):

        """ Call this method anywhere in your save override """

        for f_name, field in self.fields.items():
            if isinstance(field, RelateField):

                val = self.cleaned_data.get(f_name, {'rm': [], 'add': []})
                field.save_relations(self.instance, val, commit)

    def init_relation_fields(self):

        """ Call this in init, but AFTER calling super init """

        for f_name, field in self.fields.items():
            if isinstance(field, RelateField):
                self.fields[f_name].instance = self.instance
