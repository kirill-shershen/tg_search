from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating 'created' and 'modified'
    fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]
