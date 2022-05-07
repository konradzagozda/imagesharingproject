from django.urls import path
from rest_framework import routers

from api.views import ImageViewSet
from imagesharing import views

router = routers.DefaultRouter()
router.register('images', ImageViewSet, basename='images')

# router.register('images', ImageViewSet)