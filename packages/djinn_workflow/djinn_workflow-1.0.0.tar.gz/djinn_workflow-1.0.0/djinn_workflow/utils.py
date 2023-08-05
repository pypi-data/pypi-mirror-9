from django.contrib.contenttypes.models import ContentType
from djinn_workflow.models.modelworkflow import ModelWorkflow
from djinn_workflow.models.workflow import Workflow
from djinn_workflow.models.state import State
from djinn_workflow.models.objectstate import ObjectState
from djinn_workflow.signals import state_change


def assign_workflow(wf, ct):

    """ Assign workflow to content type """

    ModelWorkflow.objects.get_or_create(workflow=wf, content_type=ct)


def get_workflow(anything):

    """ arg should be a model, an instance or a contenttype instance """

    if not isinstance(anything, ContentType):
        anything = ContentType.objects.get_for_model(anything)

    try:
        return ModelWorkflow.objects.get(content_type=anything).workflow
    except ModelWorkflow.DoesNotExist:
        return Workflow.objects.get(is_default=True)


def get_default_workflow():

    return Workflow.objects.get(is_default=True)


def set_state(obj, state):

    """ Set obj state, without doing the actual transition. This is mainly
    useful for setting initial state, i.e. during creation """

    wf = get_workflow(obj)

    if type(state) in [str, unicode]:
        state = wf.state_set.get(name=state)

    if not get_state(obj):
        ObjectState.objects.create(
            state=state,
            object_id=obj.id,
            object_ct=ContentType.objects.get_for_model(obj)
        )
    else:
        ObjectState.objects.filter(
            object_id=obj.id,
            object_ct=ContentType.objects.get_for_model(obj)
        ).update(state=state)


def get_state(obj, assume_initial=True, fail_silently=True):

    """ If fail_siltently is True, the get_state call will return
    an empty state """

    state = None

    try:
        state = ObjectState.objects.get(
            object_id=obj.pk,
            object_ct=ContentType.objects.get_for_model(obj)).state
    except ObjectState.DoesNotExist:
        if assume_initial:

            try:
                wf = get_workflow(obj)

                obj_state = ObjectState.objects.create(
                    state=wf.initial_state,
                    object_id=obj.id,
                    object_ct=ContentType.objects.get_for_model(obj)
                )

                state = obj_state.state
            except:
                if fail_silently:
                    state = State(name="no_state")

    return state


def apply_transition(obj, trans):

    """ Apply transitions, but this is unchecked for permissions! """

    state = get_state(obj)

    if type(trans) in [str, unicode]:
        trans = state.transition_set.get(name=trans)

    set_state(obj, trans.destination)

    state_change.send(obj.__class__, instance=obj,
                      state_from=state,
                      state_to=trans.destination)
