# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-29 16:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_bot_app', '0008_weatherpicture_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherpicture',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
