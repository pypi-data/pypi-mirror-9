from django.db import models
from django.contrib.contenttypes.models import ContentType
from djinn_workflow.models.workflow import Workflow


class ModelWorkflow(models.Model):

    content_type = models.ForeignKey(ContentType, unique=True)
    workflow = models.ForeignKey(Workflow)

    def __unicode__(self):
        return "%s - %s" % (self.content_type.name, self.workflow.name)

    class Meta:

        app_label = "djinn_contenttypes"
