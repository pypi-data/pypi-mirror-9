from django.forms.fields import Field
from djinn_core.utils import object_to_urn
from relate import RelateField, UpdateRelations, UpdateRelation


def _profile_to_user_or_group(profile):

    return getattr(profile, "user", getattr(profile, "usergroup", None))


class GroupField(Field):

    """ Field for assigning roles to users or groups on a given object
    TODO: this really shouldn't extend RelateField in this way, since
    it is not a relation between content types, but a relation between
    a content type and a group/user.
    """

    def __init__(self, queryset=None, *args, **kwargs):

        super(GroupField, self).__init__(*args, **kwargs)

    def prepare_value(self, data):

        
        
