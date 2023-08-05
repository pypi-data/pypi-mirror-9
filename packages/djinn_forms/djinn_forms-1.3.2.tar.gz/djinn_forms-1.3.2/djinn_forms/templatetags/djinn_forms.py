from djinn_core.utils import urn_to_object
from django.template import Library


register = Library()


@register.inclusion_tag('djinn_forms/snippets/link.html')
def link_as_a(link):

    ctx = {}

    _link = link.split("::")[0]

    if _link.startswith("urn"):

        obj = urn_to_object(_link)

        ctx['url'] = obj.get_absolute_url()
        ctx['title'] = obj.title
    else:
        ctx['url'] = ctx['title'] = _link

    ctx['target'] = link.split("::")[1] or ""

    return ctx
