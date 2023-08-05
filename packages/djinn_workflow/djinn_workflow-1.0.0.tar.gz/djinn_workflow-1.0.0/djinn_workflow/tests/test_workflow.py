from django.test.testcases import TestCase
from djinn_workflow.models.workflow import Workflow


class WorkflowTest(TestCase):

    def setUp(self):

        pass

    def test_set_default(self):

        wf0 = Workflow.objects.create(name="test0")
        wf1 = Workflow.objects.create(name="test1")
        wf2 = Workflow.objects.create(name="test2")

        wf0.is_default = True
        wf0.save()

        self.assertTrue(wf0.is_default)
        self.assertFalse(wf1.is_default)
        self.assertFalse(wf2.is_default)

        wf1.is_default = True
        wf1.save()

        self.assertFalse(Workflow.objects.get(pk=wf0.pk).is_default)
        self.assertFalse(Workflow.objects.get(pk=wf2.pk).is_default)

        wf2.is_default = True
        wf2.save()

        self.assertFalse(Workflow.objects.get(pk=wf0.pk).is_default)
        self.assertFalse(Workflow.objects.get(pk=wf1.pk).is_default)
