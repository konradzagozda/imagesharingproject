import mimetypes
import os
import sys
from os import path

import magic
from PIL import Image
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from api.serializers import OriginalImageSerializer
from api.utils import get_mime
from imagesharing.models import OriginalImage, ThumbnailImage, ThumbnailSize

MAX_WIDTH = 999_999_999


class ImageViewSetPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'create']:
            return request.user.is_authenticated
        if view.action == 'retrieve':
            return True
        return False


class ImageViewSet(CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (ImageViewSetPermission,)
    serializer_class = OriginalImageSerializer
    queryset = OriginalImage.objects.all()

    def list(self, request):
        queryset = OriginalImage.objects.filter(owner=request.user)
        serializer = OriginalImageSerializer(queryset, many=True)
        return Response(serializer.data)

    # download image
    def retrieve(self, request, pk=None):
        instance = get_object_or_404(OriginalImage, pk=pk)
        height = request.query_params.get('height')
        content_type_file = get_mime(instance.image.path)
        ext = mimetypes.guess_extension(content_type_file, strict=True)[1:]

        if height is not None:
            # check if thumbnail should be created
            tier = request.user.tier
            thumbnail_size = get_object_or_404(tier.thumbnail_sizes, height=height)
            try:
                image = ThumbnailImage.objects.get(size=thumbnail_size, original=instance).image
            except ThumbnailImage.DoesNotExist:
                image = self._create_thumbnail(int(height), instance, ext).image
        else:
            image = instance.image

        response = HttpResponse(image.open(mode='rb'), content_type=content_type_file)
        response['Content-Disposition'] = "attachment; filename=%s" % str(image)
        response['Content-Length'] = image.size

        return response

    def perform_create(self, serializer):
        print(serializer)
        serializer.save()

    @staticmethod
    def _create_thumbnail(height, original_image, extension):
        size = (MAX_WIDTH, height)
        dir_path = 'images/thumbnails/'

        if not path.exists(dir_path):
            os.mkdir(dir_path)

        thumbnail_path = f'{dir_path}{original_image.uuid}-{height}.{extension}'

        with Image.open(original_image.image.path) as im:
            im.thumbnail(size)
            im.save(thumbnail_path, format=extension)

        thumbnail = ThumbnailImage.objects.create(
            size=ThumbnailSize.objects.get(height=height),
            original=original_image,
            image=thumbnail_path
        )

        return thumbnail


