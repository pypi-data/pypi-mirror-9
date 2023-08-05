from django.template import Library
from djinn_workflow.utils import get_state


register = Library()


@register.filter(name="state")
def state(obj):

    try:
        return get_state(obj).name
    except:
        return ""
