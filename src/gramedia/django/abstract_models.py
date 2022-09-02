import logging
import django

from autoslug import AutoSlugField
from django.db import models
from django.utils import timezone

if django.VERSION >= (4, 0):
    from django.utils.translation import gettext_lazy as _
else:
    from django.utils.translation import ugettext_lazy as _

class TimestampedModel(models.Model):
    """ An abstract model that contains information about when (and possibly, by whom) an object was last updated.

    Please note, the `modified_by` field is intended to be a human-understandable value to be returned
    by an optimistic-concurrency check failure, and **not** something like a database identifier.
    """
    created = models.DateTimeField(
        _('created'),
        auto_now_add=True,
        help_text=_('Date/time this object was created.')
    )
    modified = models.DateTimeField(
        _('modified'),
        auto_now=True,
        help_text=_('Date/time this object was last updated.')
    )
    modified_by = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Optionally identifies who last updated the object.')
    )

    class Meta:
        abstract = True


class SoftDeletableModel(models.Model):
    """ A model, which when 'deleted' via an API interface, should be flagged as is_active = false, instead
    of actually being deleted from the database.
    """
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class ManuallySortedModel(models.Model):
    """ A model, which can have it's display order manually changed via the admin interface
    """
    sort_priority = models.PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True


class BaseModel(SoftDeletableModel, TimestampedModel):
    """ Common model for most of our standard use-cases.
    """
    name = models.CharField(max_length=120)
    slug = AutoSlugField(populate_from='name', unique=True, max_length=120)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name




class MarkDeletedQuerySet(models.QuerySet):
    def delete(self):
        logger = logging.getLogger('DELETE')
        logger.info('THIS MARK DELETE')
        return super(MarkDeletedQuerySet, self).update(deleted=timezone.now())

    def hard_delete(self):
        logger = logging.getLogger('HARDDELETE')
        logger.info('THIS MARK HARD DELETE')
        return super(MarkDeletedQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted=None)

    def dead(self):
        return self.exclude(deleted=None)


class MarkDeletedManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(MarkDeletedManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return MarkDeletedQuerySet(self.model).filter(deleted=None)
        return MarkDeletedQuerySet(self.model)



class MarkDeletedModel(models.Model):
    deleted = models.DateTimeField(
        _('deleted'),
        null=True,
        blank=True,
        help_text=_('Date/time this object was deleted.')
    )
    deleted_by = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Optionally identifies who deleted the object.')
    )

    objects = MarkDeletedManager()
    all_objects = MarkDeletedManager(alive_only=False)

    class Meta:
        abstract = True
