from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.registry import CTRegistry


class AbstractUserPreferences(models.Model):

    """ Set of system Preferences per user """
    user = models.OneToOneField(User)

    class Meta:

        app_label = 'djinn_profiles'
        verbose_name = _('UserPreferences')
        verbose_name_plural = _('UserPreferences')
        abstract = True

# MJB: is dit wel nodig? Deze tabel wordt namelijk aangemaakt
#class UserPreferences(AbstractUserPreferences):
#
#    class Meta:
#        app_label = 'djinn_profiles'
#        swappable = "DJINN_USERPREFERENCES_MODEL"
#
#
#CTRegistry.register("userpreferences", {"class": UserPreferences,
#                                     "app": "djinn_profiles",
#                                     "label": _("UserPreferences"),
#                                     "filter_label": _("UserPreferences"),
#                                     "name_plural": _("userpreferences")})
