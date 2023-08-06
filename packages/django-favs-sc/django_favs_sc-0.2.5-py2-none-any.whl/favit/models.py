# -*- coding: utf-8 -*-
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .managers import FavoriteManager


class Favorite(models.Model):
    """
    """

    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'))
    target_content_type = models.ForeignKey(ContentType)
    target_object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey('target_content_type', 'target_object_id')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    objects = FavoriteManager()

    class Meta:
        ordering = ["-timestamp"]
        get_latest_by = "timestamp"
        unique_together = ("user", "target_content_type", "target_object_id")
        verbose_name = _("favorite")
        verbose_name_plural = _("favorites")

    def __unicode__(self):
        return u"{} favorited {}".format(self.user, self.target)
