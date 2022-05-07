import uuid as uuid
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
    image = models.ImageField(upload_to='userdata/images/original')


class ThumbnailImage(TimestampedModel):
    """
    When first fetched, API creates ThumbnailImages for performance later.
    """
    size = models.ForeignKey(ThumbnailSize, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='userdata/images/thumbnails')
    original = models.ForeignKey(OriginalImage, on_delete=models.CASCADE)
