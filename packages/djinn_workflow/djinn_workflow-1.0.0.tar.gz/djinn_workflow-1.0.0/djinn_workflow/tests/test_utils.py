from django.test.testcases import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from djinn_workflow.utils import (
    assign_workflow, get_workflow, set_state, get_state, apply_transition)
from djinn_workflow.models import Workflow
from djinn_workflow.signals import state_change


class UtilsTest(TestCase):

    def setUp(self):

        self.wf = Workflow.objects.create(name="test")

        active = self.wf.state_set.create(name="active")
        inactive = self.wf.state_set.create(name="inactive")

        inactive.transition_set.create(name="make_active", destination=active)
        active.transition_set.create(name="make_inactive",
                                     destination=inactive)

        self.wf.initial_state = inactive

    def test_assign_workflow(self):

        ct = ContentType.objects.get_for_model(User)

        assign_workflow(self.wf, ct)

        self.assertEquals(self.wf, get_workflow(ct))
        self.assertEquals(self.wf, get_workflow(User))

        user = User.objects.create(username="bobdobalina")

        self.assertEquals(self.wf, get_workflow(user))

    def test_get_state(self):

        ct = ContentType.objects.get_for_model(User)

        assign_workflow(self.wf, ct)

        user = User.objects.create(username="bobdobalina")

        self.assertEquals(None, get_state(user))

        set_state(user, "active")

        self.assertEquals("active", get_state(user).name)

    def test_apply_transition(self):

        ct = ContentType.objects.get_for_model(User)

        assign_workflow(self.wf, ct)

        user = User.objects.create(username="bobdobalina")

        set_state(user, "active")

        self.assertTrue(user.is_active)

        def callback(sender, instance, state_from, state_to, **kwargs):

            if state_to.name == "inactive":
                instance.is_active = False
                instance.save()

        state_change.connect(callback)

        apply_transition(user, "make_inactive")

        self.assertFalse(user.is_active)

        self.assertEquals("inactive", get_state(user).name)
