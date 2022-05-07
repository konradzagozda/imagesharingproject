import mimetypes
import os
import sys
from os import path

import magic
from PIL import Image
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response

from api.serializers import OriginalImageSerializer
from api.utils import get_mime
from imagesharing.models import OriginalImage, ThumbnailImage, ThumbnailSize, TemporaryLink

MAX_WIDTH = 999_999_999


class ImageViewSetPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'create']:
            return request.user.is_authenticated
        if view.action == 'retrieve':
            return True
        if view.action == 'get_temp_link' and request.user.tier.expiring_links:
            return True
        if view.action == 'temp':
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
        tier = instance.owner.tier

        if height is not None:
            # check if thumbnail should be created
            thumbnail_size = get_object_or_404(tier.thumbnail_sizes, height=height)
            try:
                image = ThumbnailImage.objects.get(size=thumbnail_size, original=instance).image
            except ThumbnailImage.DoesNotExist:
                image = self._create_thumbnail(int(height), instance, ext).image
        else:
            if tier.original_image:
                image = instance.image
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(image.open(mode='rb'), content_type=content_type_file)
        response['Content-Disposition'] = "attachment; filename=%s" % str(image)
        response['Content-Length'] = image.size

        return response

    @action(detail=True, methods=['get'])
    def get_temp_link(self, request, pk=None):
        """
        /api/images/<uuid>/get_temp_link/?ttl=300&height=200
        /api/images/<uuid>/get_temp_link/?ttl=300
        """
        original_image = self.get_object()
        user = request.user
        ttl = int(request.query_params.get('ttl'))
        height = request.query_params.get('height')

        if not 300 <= ttl <= 30_000:
            raise ValidationError('ttl must be between 300 and 30_000')

        if height is not None:
            try:
                thumbnail_size = user.tier.thumbnail_sizes.get(height=height)
            except ThumbnailSize.DoesNotExist:
                raise ValidationError('passed height isn\'t supported in current tier')

            # create temp link for size
            try:
                thumbnail = ThumbnailImage.objects.get(size=thumbnail_size, original=original_image)
            except ThumbnailImage.DoesNotExist:
                content_type_file = get_mime(original_image.image.path)
                ext = mimetypes.guess_extension(content_type_file, strict=True)[1:]
                thumbnail = self._create_thumbnail(int(height), original_image, ext)

            temp = TemporaryLink.objects.create(original_image=original_image, thumbnail=thumbnail, ttl=ttl)
        else:
            temp = TemporaryLink.objects.create(original_image=original_image, ttl=ttl)

        data = {
            'termination_datetime': temp.termination_datetime,
            'link': f'/api/images/temp/?uuid={temp.uuid}'
        }

        return Response(data=data)

    @action(detail=False, methods=['get'])
    def temp(self, request):
        uuid = request.query_params.get('uuid')
        link = TemporaryLink.objects.get(uuid=uuid)
        if not link.is_valid:
            raise ValidationError('link has expired')

        if link.thumbnail:
            image = link.thumbnail.image
        else:
            image = link.original_image.image

        content_type_file = get_mime(image.path)
        response = HttpResponse(image.open(mode='rb'), content_type=content_type_file)
        response['Content-Disposition'] = "attachment; filename=%s" % str(image)
        response['Content-Length'] = image.size

        return response


    @staticmethod
    def _create_thumbnail(height, original_image, extension):
        size = (MAX_WIDTH, height)
        dir_path = 'images/thumbnails/'

        if not path.exists(dir_path):
            os.mkdir(dir_path)

        thumbnail_path = f'{dir_path}{original_image.uuid}-{height}.{extension}'

        with Image.open(original_image.image.path) as im:
            im.thumbnail(size)
            format = 'jpeg' if extension == 'jpg' else extension
            im.save(thumbnail_path, format=format)

        thumbnail = ThumbnailImage.objects.create(
            size=ThumbnailSize.objects.get(height=height),
            original=original_image,
            image=thumbnail_path
        )

        return thumbnail
