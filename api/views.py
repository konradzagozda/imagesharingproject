import mimetypes

from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from api.serializers import OriginalImageSerializer
from imagesharing.models import OriginalImage


class ImageViewSetPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'create']:
            return request.user.is_authenticated
        if view.action == 'retrieve':
            return True
        return False

class ImageViewSet(viewsets.ViewSet):
    permission_classes = (ImageViewSetPermission,)

    def list(self, request):
        queryset = OriginalImage.objects.filter(owner=request.user)
        serializer = OriginalImageSerializer(queryset, many=True)
        return Response(serializer.data)

    # image download.
    def retrieve(self, request, pk=None):
        # wydaje sie ze mozna latwiej...
        instance = get_object_or_404(OriginalImage, pk=pk)
        size = request.query_params.get('size')

        image = instance.image
        content_type_file = mimetypes.guess_type(image.path)[0]
        response = HttpResponse(open(image.path, 'rb'), content_type=content_type_file)
        response['Content-Disposition'] = "attachment; filename=%s" % str(image)
        response['Content-Length'] = image.size
        if size is not None:
            # todo return thumbnail
            pass
        else:
            pass

        return response


    # image upload
    def create(self, request):
        try:
            image = request.data['image']
        except KeyError:
            raise ParseError('Request has no resource file attached')
        product = OriginalImage.objects.create(image=image)