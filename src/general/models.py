from django.db import models


class AbstractBaseModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_changed = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True
        ordering = ('-date_created',)
