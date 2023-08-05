from pgauth.models import Role
from djinn_core.utils import object_to_urn
from relate import RelateField, UpdateRelations, UpdateRelation


def _profile_to_user_or_group(profile):

    return getattr(profile, "user", getattr(profile, "usergroup", None))


class UpdateRoles(UpdateRelations):

    def __init__(self, instance, data, role):
        self.instance = instance
        self.rms = data.get('rm', [])
        self.adds = data.get('add', [])
        self.role = role

    def update(self):

        role = Role.objects.get(name=self.role)

        # Unrelate
        for profile in self.rms:
            self.instance.rm_local_role(role,
                                        _profile_to_user_or_group(profile))

        # Relate
        for profile in self.adds:
            self.instance.add_local_role(role,
                                         _profile_to_user_or_group(profile))


class UpdateRole(UpdateRelation):

    def __init__(self, instance, data, role):
        self.instance = instance
        self.tgt = data
        self.role = role

    def update(self):

        role = Role.objects.get(name=self.role)

        if self.tgt:
            self.instance.rm_local_role(role)
            self.instance.add_local_role(role,
                                         _profile_to_user_or_group(self.tgt))


class LocalRoleField(RelateField):

    """ Field for assigning roles to users or groups on a given object
    TODO: this really shouldn't extend RelateField in this way, since
    it is not a relation between content types, but a relation between
    a content type and a group/user.
    """

    updater = UpdateRoles

    def __init__(self, role_id, content_types, *args, **kwargs):

        self.role = role_id
        super(LocalRoleField, self).__init__(self.role, content_types, *args,
                                             **kwargs)

    def prepare_value(self, data):

        """ Get the existing local roles for the given role.  If
        data['rm'] has values, filter those out of the result.  If
        data['add'] has values, add those to the result
        """

        # We have an initial value set...
        #
        if data and not "add" in data.keys():
            return data

        if not data:
            data = {}

        roles = self.instance.get_local_roles(role_filter=[self.role])

        users_or_groups = [lrole.assignee for lrole in roles]

        users_or_groups = [u.profile for u in users_or_groups if u.profile]

        try:
            users_or_groups = filter(lambda x: x not in data['rm'],
                                     users_or_groups)
        except:
            pass

        try:
            users_or_groups += data['add']
        except:
            pass

        return [{'label': unicode(profile),
                 'value': object_to_urn(profile)} for profile in
                users_or_groups]


class LocalRoleSingleField(LocalRoleField):

    updater = UpdateRole

    def prepare_value(self, data):

        """ Get existing role, if it's there """

        # We have an initial value set...
        #
        if data:
            return {'label': str(data), 'value': object_to_urn(data)}

        value = super(LocalRoleSingleField, self).prepare_value(data)

        if value:
            return value[0]
        else:
            return None
