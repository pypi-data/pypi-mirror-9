from django.db import models
from django.utils.translation import ugettext_lazy as _


class State(models.Model):

    name = models.CharField(_(u"Name"), max_length=100)
    workflow = models.ForeignKey("Workflow")

    def __unicode__(self):

        return "%s" % self.name

    def get_transitions(self, obj, user):

        """Returns all allowed transitions for passed object and user.
        """

        transitions = []

        for transition in self.transition_set.all():

            permission = transition.permission

            if permission is None:
                transitions.append(transition)
            elif user.has_perm(permission.codename, obj=obj):
                transitions.append(transition)

        return transitions

    class Meta:

        ordering = ("name", )
        app_label = "djinn_workflow"
