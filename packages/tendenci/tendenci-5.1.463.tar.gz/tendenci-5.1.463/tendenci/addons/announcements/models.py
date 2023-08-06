from django.contrib.contenttypes import generic
from django.db import models
from django.utils.translation import ugettext_lazy as _
from tinymce import models as tinymce_models

from tendenci.addons.announcements.managers import EmergencyAnnouncementManager
from tendenci.core.perms.models import TendenciBaseModel
from tendenci.core.perms.object_perms import ObjectPermission


class EmergencyAnnouncement(TendenciBaseModel):
    title = models.CharField(_('Title'), max_length=250)
    content = tinymce_models.HTMLField(_('Content'))
    enabled = models.BooleanField(_('Enabled'), default=True)

    perms = generic.GenericRelation(ObjectPermission,
                                    object_id_field="object_id",
                                    content_type_field="content_type")
    objects = EmergencyAnnouncementManager()

    class Meta:
        permissions = (("view_emergencyannouncement",_("Can view emergency announcement")),)
        verbose_name = _('Emergency Announcement')
        verbose_name_plural = _('Emergency Announcements')

    def __unicode__(self):
        return self.title
