from django.db import models
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _


class Transition(models.Model):

    name = models.CharField(_(u"Name"), max_length=100)
    destination = models.ForeignKey(
        "State",
        verbose_name=_(u"Destination"),
        related_name="destination_state")
    permission = models.ForeignKey(
        Permission,
        verbose_name=_(u"Permission"), blank=True, null=True)
    state = models.ForeignKey("State")

    def __unicode__(self):

        return self.name

    class Meta:

        ordering = ("name", )
        app_label = "djinn_workflow"
