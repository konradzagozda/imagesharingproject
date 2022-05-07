import datetime
import uuid as uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import AbstractUser


# base model useful for logging changes
from django.utils import timezone


class TimestampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# reference with get_user_model()

class User(TimestampedModel, AbstractUser):
    BASIC_TIER_ID = 1
    tier = models.ForeignKey('Tier', default=BASIC_TIER_ID, on_delete=models.PROTECT)


class ThumbnailSize(TimestampedModel):
    height = models.IntegerField(help_text='height in pixels')

    def __str__(self):
        return str(self.height) + 'px'


class Tier(TimestampedModel):
    name = models.CharField(max_length=30)
    thumbnail_sizes = models.ManyToManyField(ThumbnailSize)
    expiring_links = models.BooleanField(help_text='ability to generate short-lived links', default=False)
    original_image = models.BooleanField(help_text='ability to get original-size image', default=False)

    def __str__(self):
        return self.name


class OriginalImage(TimestampedModel):
    uuid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text='helps user identify his image', null=True)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL) # if user is deleted, data could be accessible
    image = models.ImageField(upload_to='images/original')


class ThumbnailImage(TimestampedModel):
    """
    When first fetched, API creates ThumbnailImages for performance later.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size = models.ForeignKey(ThumbnailSize, on_delete=models.PROTECT)
    image = models.ImageField()
    original = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)


class TemporaryLink(TimestampedModel):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    original_image = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
    thumbnail = models.ForeignKey(ThumbnailImage, null=True, blank=True, on_delete=models.CASCADE) # if null it refers to original image

    ttl = models.IntegerField()
    termination_datetime = models.DateTimeField(null=True, blank=True)

    @property
    def is_valid(self):
        now = timezone.now()
        return now < self.termination_datetime

    def save(self, *args, **kwargs):
        if not self.termination_datetime:
            self.termination_datetime = datetime.datetime.now() + datetime.timedelta(seconds=self.ttl)
        super().save(*args, **kwargs)

    # /images/temp?uuid=<uuid>
