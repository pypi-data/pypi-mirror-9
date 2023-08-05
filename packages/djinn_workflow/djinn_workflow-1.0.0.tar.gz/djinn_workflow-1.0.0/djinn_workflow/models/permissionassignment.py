from django.db import models
from django.contrib.auth.models import Permission
from djinn_auth.models.role import Role


class PermissionAssignment(models.Model):

    """ Permission/role assignment bound to a state
    """

    state = models.ForeignKey("State")
    role = models.ForeignKey(Role)
    permission = models.ForeignKey(Permission)

    class Meta:

        app_label = "djinn_workflow"

    def __unicode__(self):

        return u"%s for %s in state %s" % (self.permission, self.role,
                                           self.state)
