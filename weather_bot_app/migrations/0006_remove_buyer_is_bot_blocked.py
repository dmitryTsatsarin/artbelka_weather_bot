# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-05 20:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weather_bot_app', '0005_auto_20170905_2001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='buyer',
            name='is_bot_blocked',
        ),
    ]