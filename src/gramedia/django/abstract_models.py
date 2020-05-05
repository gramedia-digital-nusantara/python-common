from autoslug import AutoSlugField
from django.db import models
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
    name = models.CharField(max_length=50)
    slug = AutoSlugField(populate_from='name', unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
