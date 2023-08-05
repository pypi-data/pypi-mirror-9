from django.forms.fields import Field
from djinn_forms.widgets.share import ShareWidget
from djinn_core.utils import object_to_urn


class ShareField(Field):

    """ Field for shares, inspired by RelateField """

    widget = ShareWidget

    def __init__(self, mode, content_types, *args, **kwargs):

        self.mode = mode
        self.content_types = content_types
        self.instance = None

        super(ShareField, self).__init__(*args, **kwargs)

    def save_share(self, obj, data, commit):

        """ Save shares given in the data, by keys 'rm' and 'add' """

        class UpdateShare(object):

            def __init__(self, instance, rms, adds, mode):
                self.instance = instance
                self.rms = rms
                self.adds = adds
                self.mode = mode

            def update(self):
                # Revoke share
                for tgt in self.rms:
                    self.instance.rm_share(tgt.ct_name, tgt.id, self.mode)
                # share
                for tgt in self.adds:
                    self.instance.add_share(tgt.ct_name, tgt.id, self.mode)

        share_updater = UpdateShare(
            obj, data.get('rm', []), data.get('add', []), self.mode)

        if commit:
            share_updater.update()

        else:

            # append the updater instance to the object. Note that it's a list
            # since there can be more than one relation field per instance
            if not hasattr(obj, '_share_updater'):
                obj._share_updater = []
            obj._share_updater.append(share_updater)

    def widget_attrs(self, widget):

        """Renders this field as an HTML widget."""

        attrs = super(ShareField, self).widget_attrs(widget)

        attrs.update({'content_type': self.content_types})

        return attrs

    def prepare_value(self, data):

        """ Return shares for this field. If data is empty,
        we simply get the related objects for the given type.
        If data['rm'] has values, filter those out of the result.
        If data['add'] has values, add those to the result
        """

        shares = self.instance.shares.all()

        try:
            shares = filter(lambda x: x not in data['rm'], shares)
        except:
            pass

        try:
            shares += data['add']
        except:
            pass

        prepared = []
        for rel in shares:
            if rel.user_id:
                uprofile = rel.user.profile
                prepared.append({'label': str(uprofile),
                                 'value': object_to_urn(uprofile)})
            if rel.usergroup_id:
                gprofile = rel.usergroup.profile
                prepared.append({'label': str(gprofile),
                                 'value': object_to_urn(gprofile)})
        return prepared
