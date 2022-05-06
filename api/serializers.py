from rest_framework import serializers

from imagesharing.models import OriginalImage, ThumbnailImage


class OriginalImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalImage
        fields = ['id', 'owner', 'image']


class ThumbnailImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThumbnailImage
        fields = ['id', 'owner', 'image', 'size']
