
from django.db import migrations


def create_default_tiers(apps, schema_editor):
    ThumbnailSize = apps.get_model("imagesharing", "ThumbnailSize")
    Tier = apps.get_model("imagesharing", "Tier")

    thumbnail_200 = ThumbnailSize.objects.create(height=200)
    thumbnail_400 = ThumbnailSize.objects.create(height=400)

    basic = Tier.objects.create(name='basic')
    basic.thumbnail_sizes.set([thumbnail_200])

    premium = Tier.objects.create(name='premium', original_image=True)
    premium.thumbnail_sizes.set([thumbnail_200, thumbnail_400])

    enterprise = Tier.objects.create(name='enterprise', original_image=True, expiring_links=True)
    enterprise.thumbnail_sizes.set([thumbnail_200, thumbnail_400])


def delete_default_tiers(apps, schema_editor):
    ThumbnailSize = apps.get_model("imagesharing", "ThumbnailSize")
    Tier = apps.get_model("imagesharing", "Tier")

    ThumbnailSize.objects.all().delete()
    Tier.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('imagesharing', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_tiers, reverse_code=delete_default_tiers),
    ]
