from django.forms.fields import Field
from djinn_forms.widgets.relate import RelateWidget, RelateSingleWidget
from djinn_core.utils import object_to_urn
from base import AdditionalHandlingMixin


class UpdateRelations(object):

    def __init__(self, instance, data, relation_type):

        self.instance = instance
        self.rms = data.get('rm', [])
        self.adds = data.get('add', [])
        self.relation_type = relation_type

    def update(self):

        # Unrelate
        for tgt in self.rms:

            #if callable(self.relation_type):
            #    rtype = self.relation_type(tgt)
            #else:
            rtype = self.relation_type

            self.instance.rm_relation(rtype, tgt)

        # Relate
        for tgt in self.adds:

            #if callable(self.relation_type):
            #    rtype = self.relation_type(tgt)
            #else:
            rtype = self.relation_type

            self.instance.add_relation(rtype, tgt)


class UpdateRelation(object):

    """ Updater for single relation. Existing relations are deleted """

    def __init__(self, instance, tgt, relation_type):
        self.instance = instance
        self.tgt = tgt
        self.relation_type = relation_type

    def update(self):
        if self.tgt:
            self.instance.get_relations(
                relation_type_list=[self.relation_type]).delete()
            self.instance.add_relation(self.relation_type, self.tgt)


class RelateField(Field, AdditionalHandlingMixin):

    """ Field for relations, based on """

    widget = RelateWidget
    updater = UpdateRelations

    def __init__(self, relation_type, content_types, *args, **kwargs):

        self.relation_type = relation_type
        self.content_types = content_types
        self.instance = None

        super(RelateField, self).__init__(*args, **kwargs)

    def save_relations(self, obj, data, commit):

        """ Save relations given in the data, by keys 'rm' and 'add' """

        relation_updater = self.updater(obj, data, self.relation_type)

        if commit:
            relation_updater.update()
        else:
            # append the updater instance to the object. Note that it's a list
            # since there can be more than one relation field per instance
            if not hasattr(obj, '_relation_updater'):
                obj._relation_updater = []
            obj._relation_updater.append(relation_updater)

    def widget_attrs(self, widget):

        """Renders this field as an HTML widget."""

        attrs = super(RelateField, self).widget_attrs(widget)

        attrs.update({'content_type': self.content_types})

        return attrs

    def prepare_value(self, data):

        """Return relations for this field. If data is empty, we simply get
        the related objects for the given type. If data['rm'] has
        values, filter those out of the result. If data['add'] has
        values, add those to the result.
        """

        if data is None:
            data = {}

        relations = self.instance.get_related(self.relation_type)

        relations = filter(lambda x: x not in data.get('rm', []), relations)

        relations += data.get('add', [])

        return [{'label': rel.title, 'value': object_to_urn(rel)} for rel in
                relations if rel]


class RelateSingleField(RelateField):

    widget = RelateSingleWidget
    updater = UpdateRelation

    def prepare_value(self, data):

        """ Get existing role, if it's there """

        value = super(RelateSingleField, self).prepare_value(data)

        try:
            return value[0]
        except:
            return None
