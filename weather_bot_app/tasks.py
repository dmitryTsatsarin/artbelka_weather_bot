# -*- coding: utf-8 -*-
import json
import logging

import arrow
import imgkit
import telebot as telebot_lib
from celery import shared_task
from django.conf import settings
from telebot import apihelper

from artbelka_weather_bot.celery import app
from weather_bot_app.bot_routing import initialize_bot_with_routing2
from weather_bot_app.helpers import CityEnum
from weather_bot_app.models import Bot, WeatherSchedulerResult, WeatherPicture
from weather_bot_app.models import Buyer
# import botan
from weather_bot_app.utils import create_shop_telebot, get_menu

logger = logging.getLogger(__name__)


@shared_task
def post_by_schedule(dry_run=False):

    # запускаем нотификации в этом часе
    start_datetime = arrow.now().floor('hour').datetime
    end_datetime = arrow.now().ceil('hour').datetime
    if not Bot.objects.filter(name=settings.COMMON_WEATHER_BOT_NAME).exists():
        logger.error('Bot is not found "%s"' % settings.COMMON_WEATHER_BOT_NAME)
        return

    bot = Bot.objects.filter(name=settings.COMMON_WEATHER_BOT_NAME).get()

    buyers = list(
        Buyer.objects.filter(
            bot_buyer_map_rel__bot=bot,
            bot_buyer_map_rel__is_blocked_by_user=False,
            weather_scheduler_rel__is_schedule_enabled=True,
            weather_scheduler_rel__next_notification_at__range=(start_datetime, end_datetime),

        )
    )
    for buyer in buyers:
        notification_at = buyer.weather_scheduler_rel.next_notification_at
        PostWeatherTask().apply_async(kwargs=dict(
            bot_id=bot.id,
            buyer_id=buyer.id,
            notification_at=notification_at,
        ))

        logger.info(u'Запущен post_by_schedule к buyer=(%s, %s)' % (buyer.id, buyer.full_name))
        timezone = CityEnum.get_time_zone(buyer.city)
        tomorrow = buyer.weather_scheduler_rel.get_tomorrow(timezone)
        buyer.weather_scheduler_rel.next_notification_at = tomorrow.datetime
        buyer.weather_scheduler_rel.save()


class CommonBaseTask(app.Task):
    "основа для таски, непривязываясь(!) к конкретному боту"

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if settings.DEBUG:
            logger.debug(exc, exc_info=True)
        else:
            logger.exception(exc)
            raise

    def run(self, *args, **kwargs):
        return self.run_core(*args, **kwargs)


class BotBaseTask(CommonBaseTask):
    "Основа для таски в привязке к боту"
    shop_telebot = None

    def run(self, bot_id, *args, **kwargs):
        try:
            if Bot.objects.filter(id=bot_id).exists():
                bot = Bot.objects.filter(id=bot_id).get()
                self.shop_telebot = create_shop_telebot(bot.telegram_token)
                return self.run_core(*args, **kwargs)
            else:
                logger.error('Token "%s" is not found' % bot_id)

        except Exception as e:
            if settings.DEBUG:
                logger.debug(e, exc_info=True)
            else:
                logger.exception(e)
                raise


class CollectorTask(app.Task):
    queue = 'collector'

    def _custom_de_json(self, json_string):
        try:
            data_dict = json.loads(json_string)
        except ValueError as e:
            data_dict = {}
        return data_dict

    def run(self, token, json_string, message_created_at, **kwargs):
        try:
            update = telebot_lib.types.Update.de_json(json_string)
            update.sys_message_created_at = message_created_at
            update.sys_message_received_at = arrow.now().datetime
            request_dict = self._custom_de_json(json_string)
            logger.info(u'data=%s' % json_string.decode('unicode-escape'))

            if update.callback_query:
                chat_id = update.callback_query.message.chat.id
                event_name = update.callback_query.data
            elif update.message:
                chat_id = update.message.chat.id
                event_name = update.message.text
            elif request_dict.has_key('channel_post') or request_dict.has_key('edited_channel_post'):
                # пока игнорируем сообщения из каналов
                logger.info(u'Проигнорировано сообщение из channel %s' % json_string.decode('unicode-escape'))
                return
            else:
                raise Exception('chat_id is not found')

            if Bot.objects.filter(telegram_token=token).exists():
                #MetricTask().apply_async(args=[chat_id, request_dict, event_name])
                shop_telebot = initialize_bot_with_routing2(token, chat_id)
                shop_telebot.process_new_updates([update])
            else:
                logger.error('Token "%s" is not found' % token)
        except Exception as e:
            if settings.DEBUG:
                logger.debug(e, exc_info=True)
            else:
                logger.exception(e)
                raise


class PostWeatherTask(BotBaseTask):
    queue = 'post_weather'

    def send_weather(self, buyer):
        weather_picture = WeatherPicture.get_weather_picture(buyer)
        chat_id = buyer.telegram_user_id
        if weather_picture:
            text_out = u'Доброе утро. Погода в %s' % weather_picture.city.capitalize()
            self.shop_telebot.send_message(chat_id, text_out, reply_markup=get_menu())
            image_file = weather_picture.get_picture_file()
            self.shop_telebot.send_photo(chat_id, image_file, reply_markup=get_menu())
        else:
            text_out = u'К сожалению прогноз погоды для %s не найден' % buyer.city
            logger.warning(text_out)
            self.shop_telebot.send_message(chat_id, text_out, reply_markup=self.menu_markup)

    def run_core(self, buyer_id=None, notification_at=None):
        logger.info(u'PostWeatherTask. Start. buyer_id=%s, notification_at=%s' % (buyer_id, notification_at))

        buyer = Buyer.objects.get(id=buyer_id)

        try:
            self.send_weather(buyer)
            WeatherSchedulerResult.objects.create(
                is_sent=True,
                buyer=buyer,
                notification_at=notification_at
            )

        except apihelper.ApiException as e:
            error_msg = 'Forbidden: bot was blocked by the user'
            if e.result.status_code == 403 and error_msg in e.result.text:
                msg = u'Пользователь %s (id=%s) заблокировал бота' % (buyer.full_name, buyer.telegram_user_id)
                logger.info(msg)
                buyer.is_bot_blocked = True
                buyer.save()


class GetWeatherTask(CommonBaseTask):
    queue = 'get_weather'

    def run_core(self, buyer_id=None, notification_at=None):
        options = {
            'format': 'png',
            'crop-h': '300',
            'crop-w': '500',
            'crop-x': '30',
            'crop-y': '520',
            'javascript-delay': '1000',
        }

        cities = CityEnum.values()
        for city in cities:
            print 'Вытаскиваем информацию для %s' % city
            url = CityEnum.grab_map[city]
            now = arrow.now()
            filename = '%s_%s.%s' % (city, now.isoformat(), options['format'])
            fullfilename = '%s/%s' % (settings.MEDIA_ROOT, filename)
            try:
                result = imgkit.from_url(url, fullfilename, options=options)
            except Exception as e:
                wrong_wkhtmltoimage_error = 'Exit with code 1 due to network error: HostNotFoundError'
                if wrong_wkhtmltoimage_error in e.message:
                    logger.info('Неверная ошибка wkhtmltoimage с запятой в урле: %s' % wrong_wkhtmltoimage_error)
                else:
                    raise e

            WeatherPicture.objects.create(created_at=now.datetime, city=city, picture=filename)


# class MetricTask(app.Task):
#     queue = 'metric'
#
#     def run(self, uid, message_dict, event_name, **kwargs):
#         try:
#             # uid = message.from_user
#             # message_dict = message.to_dict()
#             # event_name = update.message.text
#
#             result = botan.track(settings.BOTAN_TOKEN, uid, message_dict, event_name)
#             if result and result['status'] and 'accepted' not in result['status']:
#                 logger.warning('Something wrong with metrics: %s' % result)
#             logger.info(result)
#
#         except Exception as e:
#             if settings.DEBUG:
#                 logger.debug(e, exc_info=True)
#             else:
#                 logger.exception(e)
#                 raise
