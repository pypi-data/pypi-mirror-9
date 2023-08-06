from django.db import models


__all__ = ['VisibilityManager', 'VisibilityManagerMixin']


class VisibilityManagerMixin(object):
    """
    This manager should be used with a model that implements the Hideable
    mixin.
    """

    def __init__(self, *args, **kwargs):
        self.visible = kwargs.pop('visible')
        super(VisibilityManagerMixin, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(hidden__isnull=self.visible)


class VisibilityManager(VisibilityManagerMixin, models.Manager):
    pass
