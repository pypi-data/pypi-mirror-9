from django.db import models
from django.utils.translation import ugettext_lazy as _
from djinn_contenttypes.registry import CTRegistry
from djinn_contenttypes.models.sharing import SharingMixin


class AbstractGroupProfile(models.Model):

    name = models.CharField(_('Name'), max_length=100)

    class Meta:

        app_label = 'djinn_profiles'
        verbose_name = _('GroupProfile')
        verbose_name_plural = _('GroupProfiles')
        abstract = True


class GroupProfile(AbstractGroupProfile, SharingMixin):

    class Meta:
        app_label = 'djinn_profiles'
        swappable = "DJINN_GROUPPROFILE_MODEL"


CTRegistry.register("groupprofile", {"class": GroupProfile,
                                     "app": "djinn_profiles",
                                     "label": _("Group"),
                                     "filter_label": _("Groups"),
                                     "name_plural": _("groupprofiles")})
