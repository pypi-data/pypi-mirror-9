from django.db.models.signals import post_save
from django.dispatch import receiver
from djinn_workflow.models.workflow import Workflow


@receiver(post_save, sender=Workflow)
def workflow_post_save(sender, instance, **kwargs):

    if instance.is_default:
        Workflow.objects.all().exclude(pk=instance.pk).update(is_default=0)
