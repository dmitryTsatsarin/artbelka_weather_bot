# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import arrow
from django.db import models
from django.contrib.auth import get_user_model
from os.path import splitext
import uuid
from weather_bot_app.helpers import CityEnum

User = get_user_model()


def rename_and_upload_path(instance, filename):
    _, ext = splitext(filename)

    base_filename = str(uuid.uuid4())

    return 'product_photo/%s%s' % (base_filename, ext)


def postponed_post_path(instance, filename):
    _, ext = splitext(filename)

    base_filename = str(uuid.uuid4())

    return 'postponed_post/%s%s' % (base_filename, ext)


def faq_path(instance, filename):
    _, ext = splitext(filename)

    base_filename = str(uuid.uuid4())

    return 'faq/%s%s' % (base_filename, ext)


class BotBuyerMap(models.Model):
    buyer = models.ForeignKey('Buyer', related_name='bot_buyer_map_rel')
    bot = models.ForeignKey('Bot', related_name='bot_buyer_map_rel')
    created_at = models.DateTimeField(auto_now_add=True)
    is_blocked_by_user = models.BooleanField(default=False)
    dialog_with_support = models.TextField(null=True)

    def __unicode__(self):
        return u'%s <-> %s' % (self.bot.name, self.buyer.full_name)


class Buyer(models.Model):
    first_name = models.CharField(max_length=255, default='')
    last_name = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=50, null=True)
    telegram_user_id = models.BigIntegerField(null=True)

    city = models.CharField(choices=CityEnum.for_choice(), default=CityEnum.MOSCOW, max_length=255)
    hour = models.IntegerField(default=0)
    minute = models.IntegerField(default=0)

    @property
    def full_name(self):
        return u'%s %s' % (self.first_name, self.last_name)

    def __unicode__(self):
        return u'%s %s %s' % (self.first_name, self.last_name, self.telegram_user_id)


class EnabledManager(models.Manager):
    def get_queryset(self):
        return super(EnabledManager, self).get_queryset().filter(is_schedule_enabled=True)


class WeatherPicture(models.Model):
    city = models.CharField(choices=CityEnum.for_choice(), default=CityEnum.MOSCOW, max_length=255)
    created_at = models.DateTimeField()
    picture = models.ImageField(null=True)

    def get_picture_file(self):
        image_file = open(self.picture.path)
        return image_file

    @staticmethod
    def get_weather_picture(buyer):
        return WeatherPicture.objects.filter(city=buyer.city, created_at__gte=arrow.now().shift(hours=-24).datetime).order_by('-created_at').first()


class WeatherScheduler(models.Model):
    buyer = models.OneToOneField(Buyer, related_name='weather_scheduler_rel')
    next_notification_at = models.DateTimeField()
    is_schedule_enabled = models.BooleanField(default=False)

    objects = models.Manager()
    qs_enabled = EnabledManager()

    def get_tomorrow(self, timezone):
        tomorrow = arrow.now(tz=timezone).shift(days=1).replace(hour=self.buyer.hour, minute=self.buyer.minute, second=0)
        return tomorrow


class WeatherSchedulerResult(models.Model):
    buyer = models.ForeignKey(Buyer)
    #weather_scheduler = models.ForeignKey(WeatherScheduler)
    notification_at = models.DateTimeField()
    is_sent = models.BooleanField(default=False, verbose_name=u'Отправлено')
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.id



class BotAdministratorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return u'%s' % self.user.username


class Bot(models.Model):
    administrator = models.ForeignKey(User, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    telegram_token = models.CharField(max_length=255, null=True, blank=True)
    order_email = models.EmailField(null=True, help_text='Сюда будет отправляться информация о заказе')
    bot_support = models.ForeignKey(Buyer, null=True, blank=True, help_text='Человек, которому будут перенаправляться все вопросы из бота')
    hello_description = models.CharField(max_length=1000, default='', help_text='Начальное описание после /start')
    #is_bot_for_testing = models.BooleanField(default=True)
    #telegram_token_test = models.CharField(max_length=255, null=True, blank=True, help_text=u'Токен телеграмма для тестрования')

    def __unicode__(self):
        return u'%s' % self.name

    def save(self, *args, **kwargs):
        from django.contrib.auth.models import Group

        group_name = 'bot_administrator_group'
        group = Group.objects.filter(name=group_name).get()
        if not self.administrator:
            username = '%s%s' % (self.name, 'Administrator')
            password = User.objects.make_random_password()
            user = User.objects.create_user(username=username, password=password, is_staff=True)
            BotAdministratorProfile.objects.create(user_id=user.id)
            user.groups.add(group)
            self.administrator = user

        super(Bot, self).save(*args, **kwargs)

        from weather_bot_app.helpers import initialize_webhook_for_bot
        initialize_webhook_for_bot(self.telegram_token)


class MessageLog(models.Model):
    message_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    buyer = models.ForeignKey(Buyer, null=True, blank=True)
    bot = models.ForeignKey(Bot, null=True, blank=True)

    def __unicode__(self):
        return self.message_text

# подумать о добавлении, или попробовать logstash
# class SystemLog(models):
#     time_execution =
#     time_in_queue =
#     full_time =


