from django.db import models
from django.contrib.auth.models import AbstractUser


# base model useful for logging changes
class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# reference with get_user_model()

class User(TimestampedModel, AbstractUser):
    tier = models.ForeignKey('Tier', on_delete=models.PROTECT) # make sure user belongs to other tier before deleting it.


class ThumbnailSize(TimestampedModel):
    height = models.IntegerField(help_text='height in pixels')


class Tier(TimestampedModel):
    name = models.CharField(max_length=30)
    thumbnail_sizes = models.ManyToManyField(ThumbnailSize)
    expiring_links = models.BooleanField(help_text='ability to generate short-lived links', default=False)
    original_image = models.BooleanField(help_text='ability to get original-size image', default=False)



