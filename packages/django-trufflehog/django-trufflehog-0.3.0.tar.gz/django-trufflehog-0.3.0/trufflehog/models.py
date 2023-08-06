from django.db import models

import datetime
import functools

from django.db import models
from django.utils import timezone

from django.utils.translation import ugettext_lazy as _


__all__ = ('DateTraceable', 'Hideable')


class DateTraceable(models.Model):
    """
    An abstract model mixin that let's you trace the date of creation and
    updating.
    """

    created = models.DateTimeField(
        editable=False,
        verbose_name=_("date created")
    )
    updated = models.DateTimeField(
        editable=False,
        verbose_name=_("date updated")
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        now = timezone.now()
        if not self.pk:
            self.created = now
        self.updated = now
        super().save(*args, **kwargs)

class Hideable(models.Model):
    """
    An abstract model mixin that let's you trace date and time of hiding
    (pseudo-deletion).
    """

    hidden = models.DateTimeField(
        null=True,
        editable=False,
        verbose_name=_("date hidden"),
        db_index=True,
    )

    class Meta:
        abstract = True

    @property
    def is_hidden(self):
        return self.hidden is not None

    def hide(self):
        now = timezone.now()
