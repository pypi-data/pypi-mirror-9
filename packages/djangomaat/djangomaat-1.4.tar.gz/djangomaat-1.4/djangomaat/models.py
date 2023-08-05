from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class MaatRanking(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    typology = models.CharField(max_length=255, db_index=True)
    usable = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        # This index is fundamental to avoid MySQL filesorting.
        # The first portion of the index is used to filter rows and, being
        # constant, the second can be used to order:
        # http://dev.mysql.com/doc/refman/5.0/en/order-by-optimization.html
        unique_together = ('content_type', 'typology', 'usable', 'position')

    def __str__(self):
        return 'Rank for {}'.format(self.content_object)
