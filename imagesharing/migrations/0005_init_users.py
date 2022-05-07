from django.contrib.auth import get_user_model
from django.db import migrations

from imagesharing.models import Tier

User = get_user_model()

def init_users(apps, schema_editor):
    admin = User(
        username='admin',
        is_staff=True,
        is_superuser=True,
    )
    admin.set_password('admin')
    admin.save()

    for tier in ('basic', 'premium', 'enterprise'):
        user = User(
            username=tier
        )
        user.set_password(tier)
        user.tier = Tier.objects.get(name=tier)
        user.save()


def delete_users(apps, schema_editor):
    User.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('imagesharing', '0004_rename_size_temporarylink_thumbnail'),
    ]

    operations = [
        migrations.RunPython(init_users, reverse_code=delete_users),
    ]
