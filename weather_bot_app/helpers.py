# -*- coding: utf-8 -*-
from urlparse import urlparse

from django.core.cache import cache
from django.core.files.images import ImageFile
from django.core.mail import send_mail
from django.http import QueryDict
from django.template import loader
from django.utils.http import urlencode
from telebot import types



__author__ = 'forward'

import logging
logger = logging.getLogger(__name__)

from weather_bot_app.utils import create_shop_telebot

from django.conf import settings


def initialize_all_webhooks():
    from weather_bot_app.models import Bot

    print 'Инициализация начата'
    bots = list(Bot.objects.all())
    for bot in bots:
        shop_telebot = create_shop_telebot(bot.telegram_token)
        shop_telebot.remove_webhook()

        # Ставим заново вебхук
        url = get_webhook_url(bot.telegram_token)
        print 'bot = %s, url=%s' % (bot.name, url)
        shop_telebot.set_webhook(url=url)
    print 'Инициализация закончена'


def initialize_one_webhook(bot_name):
    from weather_bot_app.models import Bot

    print 'Инициализация начата'
    bot = Bot.objects.filter(name=bot_name).get()
    shop_telebot = create_shop_telebot(bot.telegram_token)
    shop_telebot.remove_webhook()

    # Ставим заново вебхук
    url = get_webhook_url(bot.telegram_token)
    print 'bot = %s, url=%s' % (bot.name, url)
    shop_telebot.set_webhook(url=url)
    print 'Инициализация закончена'

def initialize_webhook_for_bot(token):
    print 'Инициализация начата'
    shop_telebot = create_shop_telebot(token)
    shop_telebot.remove_webhook()

    # Ставим заново вебхук
    url = get_webhook_url(token)
    print 'url=%s' % url
    shop_telebot.set_webhook(url=url)
    print 'Инициализация закончена'


def get_webhook_url(token):
    return "%s/webhooks/%s/" % (settings.WEBHOOK_URL_BASE, token)


# def send_mail_to_the_shop(order):
#
#     shop_administrator_email = order.product.bot.order_email
#     artbelka_administrator_email = settings.EMAIL_SHOP_BOT_ADMIN
#
#     thumb_url = order.product.picture['400x400'].url
#
#     context = {
#         'order_id': order.id,
#         'product_picture': "%s%s" % (settings.WEBSITE_BASE_URL, thumb_url),
#         'product_name': order.product.name,
#         'product_description': order.product.description,
#         'product_price': order.product.price,
#         'buyer_name': '%s %s' % (order.buyer.first_name, order.buyer.last_name),
#         'buyer_phone': order.buyer.phone
#     }
#
#     html_message = loader.render_to_string('order_mail.html', context)
#     text = ''
#     logger.debug('Отправка письма')
#     if shop_administrator_email:
#         send_mail(u'От бота артбелки', text, settings.EMAIL_FULL_ADDRESS, [shop_administrator_email], html_message=html_message)
#     else:
#         logger.warning(u'Осуществлен заказ id=%s, но не указан email для заказов. Нужно срочно узнать кто владелец бота' % order.id)
#     send_mail(u'От бота артбелки', text, settings.EMAIL_FULL_ADDRESS, [artbelka_administrator_email], html_message=html_message)
#     logger.debug('письмо отправлено')


class Smile(object):
    SMILING_FACE_WITH_SMILING_EYE = u"\U0001F60A"
    QUESTION = u"\U00002753"
    HANDBAG = u"\U0001F45C"
    DELIVERY_TRUCK = u'\U0001F69A'
    HIGH_VOLTAGE = u'\U000026A1'
    MEGAPHONE = u'\U0001F4E3'
    CROSS_MARK = u"\U0000274C"
    WHITE_HEAVY_CHECK_MARK = u"\U00002705"


class ChoiceEnum(object):

    @classmethod
    def for_choice(cls):
        return [(v, k) for k, v in cls.__dict__.iteritems() if k.isupper()]

    @classmethod
    def values(cls):
        return [v for k, v in cls.__dict__.iteritems() if k.isupper()]

    @classmethod
    def get_name(cls, value):
        for k, v in cls.__dict__.iteritems():
            if v == value and k.isupper():
                return k
        raise ValueError('%s is not defined' % value)


class TextCommandEnum(ChoiceEnum):
    #GET_CATALOG = u'/get_catalog'
    #GET_PRODUCT = u'/get_it_'
    #GET_PRODUCT_CONFIRM = u'/get_it2_'
    BACK = u'назад'

    #SALE = u'%s Распродажа' % Smile.HIGH_VOLTAGE
    #BACK_TO_PREVIOUS_CATALOG = u'back_to_previous_catalog'
    QUESTION_TO_ADMIN = u'%s Задать вопрос' % Smile.MEGAPHONE
    QUESTION_ABOUT_PRODUCT = u'/question_about_product'
    CLOSE_QUESTION_MODE = u'закончить разговор'

    WEATHER = u'%s Погода' % Smile.HANDBAG
    SCHEDULE = u'%s Установить расписание' % Smile.HIGH_VOLTAGE
    SCHEDULE_SAVE = u'/schedule_save'
    SETTINGS = u'%s Настройки (выбрать город)' % Smile.DELIVERY_TRUCK

    LOCATION = u'/location'


class CityEnum(ChoiceEnum):
    MINSK = 'minsk'
    MOSCOW = 'moscow'
    PITER = 'piter'
    KIEV = 'kiev'

    timezones = {
        MINSK: 'Europe/Minsk',
        MOSCOW: 'Europe/Moscow',
        PITER: 'Europe/Moscow',
        KIEV: 'Europe/Kiev'
    }

    grab_map = {
        MINSK: 'http://rp5.by/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%B8%D0%BD%D1%81%D0%BA%D0%B5,_%D0%91%D0%B5%D0%BB%D0%B0%D1%80%D1%83%D1%81%D1%8C',
        MOSCOW: 'http://rp5.by/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B5_(%D1%86%D0%B5%D0%BD%D1%82%D1%80,_%D0%91%D0%B0%D0%BB%D1%87%D1%83%D0%B3)',
        PITER: 'http://rp5.by/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3%D0%B5',
        KIEV: 'http://rp5.by/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%9A%D0%B8%D0%B5%D0%B2%D0%B5,_%D0%A3%D0%BA%D1%80%D0%B0%D0%B8%D0%BD%D0%B0',
    }

    @classmethod
    def is_this_city_exist(cls, city):
        return city.lower() in cls.__dict__.values()

    @classmethod
    def get_time_zone(cls, city):
        return cls.timezones[city]


class KeyValue(object):
    def __init__(self, cache_key, data_dict):
        self.cache_key = cache_key
        self._data = data_dict

    def __unicode__(self):
        return self.cache_key

    def __str__(self):
        return self.cache_key

    @property
    def data(self):
        return self._data

    def get_cache_key(self):
        return self.cache_key


# TODO: объединить эти 2 класса ####################################
class CacheKey(object):
    QUESTION_ABOUT_PRODUCT_ID = 'question_about_product_id'
    NEED_PHONE = 'need_phone'
    LAST_CATALOG_URI = 'last_catalog_uri'
    ORDER_ID = 'order_id'
    PRODUCT_ID = 'product_id'


class CacheKeyValue(object):
    QUESTION_MODE = KeyValue('question_mode', {
        'product_id': None,
        'is_buyer_notified': False
    })

# ####################################################################


class TsdRegExp(object):
    FIND_USER_IN_REPLY = '\(id=(\d+)\)'


def get_request_data(request):
    if hasattr(request, 'request_data'):
        return request.request_data
    request_data = request.body.decode('utf-8')
    request.request_data = request_data
    return request_data


# def generate_and_send_discount_product(product, shop_telebot, message):
#     image_file = ImageFile(product.picture)
#     order_command = u'/get_it_%s' % product.id
#     caption = u'%s\n%s\nТОРОПИТЕСЬ ТОВАР НА СКИДКЕ' % (product.name, product.description)
#
#     markup = types.InlineKeyboardMarkup()
#     callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
#     markup.add(callback_button)
#
#     shop_telebot.send_photo(message.chat.id, image_file, caption=caption, reply_markup=markup)


def get_query_dict(uri):
    if '?' in uri:
        query_dict = QueryDict(urlparse(uri).query)
    else:
        query_dict = QueryDict(uri)
    return query_dict


def create_uri(url, **params):
    return "%s?%s" % (url, urlencode(params))


class CacheAsSession(object):
    chat_id = None

    def __init__(self, chat_id):
        self.chat_id = chat_id

    def set(self, *arg, **kwargs):
        kwargs['version'] = kwargs.pop('chat_id', None) or self.chat_id
        return cache.set(*arg, **kwargs)

    def get(self, *arg, **kwargs):
        kwargs['version'] = kwargs.pop('chat_id', None) or self.chat_id
        return cache.get(*arg, **kwargs)

    def delete(self, *arg, **kwargs):
        kwargs['version'] = self.chat_id
        return cache.delete(*arg, **kwargs)

