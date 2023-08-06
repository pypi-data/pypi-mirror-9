# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models, migrations


def set_user_tz_null(apps, schema_editor):
    UserProfile = apps.get_model('dcbase', 'UserProfile')
    for profile in UserProfile.objects.all():
        profile.timezone = None
        profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ('dcbase', '0003_userprofile_timezone_null'),
    ]

    operations = [
        migrations.RunPython(set_user_tz_null)
    ]
