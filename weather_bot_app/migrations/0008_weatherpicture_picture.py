# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-29 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_bot_app', '0007_auto_20171029_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='weatherpicture',
            name='picture',
            field=models.ImageField(null=True, upload_to=b''),
        ),
    ]
