# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import arrow
import factory
from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from mock import patch

from weather_bot_app import models
from weather_bot_app.tasks import post_by_schedule


class BuyerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Buyer


class BotBuyerMapFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.BotBuyerMap


class BotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Bot


class WeatherSchedulerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.WeatherScheduler


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = settings.AUTH_USER_MODEL


def empty_func(*args, **kwargs):
    print('I am here')


def fake_send_message(text_out, *args, **kwargs):
    return text_out


class PostByScheduleTestCase(TestCase):

    @patch('weather_bot_app.helpers.initialize_webhook_for_bot', new=empty_func)
    def setUp(self):
        user = UserFactory.create()
        group = GroupFactory.create(name='bot_administrator_group')
        user.groups.add(group)

        bot = BotFactory.create(name=settings.COMMON_WEATHER_BOT_NAME)
        buyer = BuyerFactory.create(telegram_user_id=settings.ADMIN_TELEGRAM_DEFAULT_CHAT_ID)
        BotBuyerMapFactory.create(bot=bot, buyer=buyer)

        next_notification_at = arrow.now().datetime
        WeatherSchedulerFactory.create(buyer=buyer, is_schedule_enabled=True, next_notification_at=next_notification_at)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    @patch('weather_bot_app.utils.ShopTeleBot.send_message')
    def test_ok_post_by_schedule(self, mock_obj):
        post_by_schedule()
        text_out = u'Отправка погоды. Бла бла бла'
        self.assertTrue(text_out in mock_obj.call_args[0])

