from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse

from api.utils import get_mime, get_mime_memory_file
from imagesharing.models import OriginalImage, ThumbnailImage, TemporaryLink


class OriginalImageSerializer(serializers.ModelSerializer):
    links = serializers.SerializerMethodField()

    class Meta:
        model = OriginalImage
        fields = ['uuid', 'name', 'image', 'links']

    def get_links(self, obj):
        tier = obj.owner.tier
        links = OrderedDict()
        base_url = reverse('images-list')

        if tier.original_image:
            links['orig'] = f'{base_url}{obj.pk}/'

        for size in tier.thumbnail_sizes.all():
            links[str(size)] = f'{base_url}{obj.pk}/?height={size.height}'

        if tier.expiring_links:
            temp_array = []

            for link in TemporaryLink.objects.filter(original_image=obj):
                if link.is_valid:
                    key = str(link.thumbnail.size) if link.thumbnail else 'orig'
                    expire = link.termination_datetime
                    link = f'/api/images/temp/?uuid={link.uuid}'

                    temp_array.append({
                        key: (expire, link)
                    })

            links['temp'] = temp_array


        return links

    def validate_image(self, image):
        mime = get_mime_memory_file(image)
        if mime in ['image/jpeg', 'image/png']:
            return image
        raise serializers.ValidationError('Only jpeg and png formats are supported')

    def create(self, validated_data):
        validated_data['owner'] = self.context.get('request').user
        return super().create(validated_data)
