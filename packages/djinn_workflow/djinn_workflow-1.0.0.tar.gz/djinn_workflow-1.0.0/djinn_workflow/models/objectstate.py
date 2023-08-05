from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from djinn_workflow.models.state import State


class ObjectState(models.Model):

    object_ct = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('object_ct', 'object_id')
    state = models.ForeignKey(State)

    def __unicode__(self):
        return "%s - %s" % (self.content_object, self.state)

    class Meta:
        app_label = "djinn_workflow"
        unique_together = ("object_ct", "object_id")
