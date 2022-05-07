from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse

from imagesharing.models import OriginalImage, ThumbnailImage


class OriginalImageSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = OriginalImage
        fields = ['uuid', 'name', 'owner', 'image', 'links']

    def get_links(self, obj):
        tier = obj.owner.tier
        links = OrderedDict()
        base_url = reverse('images-list')

        if tier.original_image:
            links['orig'] = f'{base_url}{obj.pk}/'

        for size in tier.thumbnail_sizes.all():
            links[str(size)] = f'{base_url}{obj.pk}/?height={size.height}'

        return links


# class ThumbnailImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ThumbnailImage
#         fields = ['id', 'owner', 'image', 'size']
