from django.test import TestCase

# Create your tests here.
from imagesharing.models import Tier, ThumbnailSize


class TiersCreatedTests(TestCase):
    def test_tiers_created(self):
        self.assertEqual(3, Tier.objects.all().count())


    def test_thumbnail_sizes_created(self):
        self.assertEqual(2, ThumbnailSize.objects.all().count())