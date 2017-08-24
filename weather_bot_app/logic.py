# -*- coding: utf-8 -*-
import logging
import re

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.db.models import F, Value
from django.db.models.functions import Concat
from telebot import types, apihelper

from weather_bot_app.helpers import TextCommandEnum, send_mail_to_the_shop, generate_and_send_discount_product, get_query_dict, create_uri, CacheKey, Smile, CacheAsSession, CacheKeyValue, \
    TsdRegExp, CityEnum
from weather_bot_app.models import Buyer,Bot, BotBuyerMap, MessageLog
from weather_bot_app.utils import create_shop_telebot

logger = logging.getLogger(__name__)
to_log = logger.info


def send_schedule_product(telegram_user_id, postponed_post):
    pass
    # product_id = postponed_post.product_id
    # post_description = postponed_post.description
    #
    # shop_telebot = create_shop_telebot(postponed_post.bot.telegram_token)
    # if product_id:
    #     product = Product.objects.filter(id=product_id).get()
    #
    #     image_file = product.get_400x400_picture_file()
    #
    #     order_command = u'/get_it_%s' % product.id
    #     caption = u'%s\nНаименование: %s\nОписание: %s\nЦена: %s' % (post_description, product.name, product.description, product.price)
    #
    #     markup = types.InlineKeyboardMarkup()
    #     callback_button = types.InlineKeyboardButton(text=u"Заказать", callback_data=order_command)
    #     markup.add(callback_button)
    #
    #     shop_telebot.send_photo(telegram_user_id, image_file, caption=caption, reply_markup=markup, disable_notification=True)
    # elif postponed_post.picture:
    #     image_file = postponed_post.get_400x400_picture_file()
    #     caption = u'%s\n%s' % (postponed_post.title, post_description)
    #
    #     shop_telebot.send_photo(telegram_user_id, image_file, caption=caption, disable_notification=True)
    # else:
    #     shop_telebot.send_message(telegram_user_id, text="%s\n%s" % (postponed_post.title, post_description), disable_notification=True)


class BotView(object):
    shop_telebot = None
    menu_markup = None
    token = None
    bot_id = None

    def __init__(self, token, chat_id):
        self.token = token
        menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        menu_markup.row(TextCommandEnum.WEATHER, TextCommandEnum.SCHEDULE)
        menu_markup.row(TextCommandEnum.SETTINGS, TextCommandEnum.QUESTION_TO_ADMIN)
        self.menu_markup = menu_markup

        close_product_dialog_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        close_product_dialog_markup.row(u'Закончить разговор')
        self.close_product_dialog_markup = close_product_dialog_markup

        shop_telebot = create_shop_telebot(token)
        self.shop_telebot = shop_telebot
        self.chat_id = chat_id
        self.pseudo_session = CacheAsSession(chat_id)

        bot = Bot.objects.get(telegram_token=token)
        self.bot_id = bot.id
        self.bot_support_chat_id = settings.ADMIN_TELEGRAM_DEFAULT_CHAT_ID
        if bot.bot_support:
            self.bot_support_chat_id = bot.bot_support.telegram_user_id

    # Обработчик команд '/start'
    def handle_start_help(self, message):
        telegram_user_id = message.chat.id
        # create buyer
        bot = Bot.objects.filter(telegram_token=self.token).get()
        try:
            BotBuyerMap.objects.filter(buyer__telegram_user_id=telegram_user_id, bot=bot).get()
        except BotBuyerMap.DoesNotExist as e:
            first_name = message.chat.first_name or ''
            last_name = message.chat.last_name or ''
            buyer, _ = Buyer.objects.get_or_create(telegram_user_id=telegram_user_id, defaults=dict(
                        first_name=first_name,
                        last_name=last_name,
                        telegram_user_id=telegram_user_id
                )
            )
            BotBuyerMap.objects.create(bot=bot, buyer=buyer)

        text_out = bot.hello_description
        self.shop_telebot.send_message(message.chat.id, text_out, parse_mode='markdown')

        self.shop_telebot.send_message(message.chat.id, "Сделайте ваш выбор:", reply_markup=self.menu_markup)

    def handle_weather_now(self, message):
        text_out = 'Сегодня у нас бла бла бла бла погода'
        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.menu_markup)

    def handle_choose_city(self, message):
        text_out = u'На данный момент у меня есть информация только об этих городах:'
        markup = types.InlineKeyboardMarkup()
        buttons = [
            # внимание, нельзя пробрасывать знак "-" в качестве callback_data (telegram ругается)
            (
                ('Минск', create_uri(TextCommandEnum.LOCATION, city=CityEnum.MINSK)),
                ('Москва', create_uri(TextCommandEnum.LOCATION, city=CityEnum.MOSCOW)),
            ),
            (
                ('Санкт-Петербург', create_uri(TextCommandEnum.LOCATION, city=CityEnum.PITER)),
                ('Киев', create_uri(TextCommandEnum.LOCATION, city=CityEnum.KIEV)),
            )
        ]

        for row in buttons:
            city_buttons = []
            for city, uri in row:
                city_buttons.append(types.InlineKeyboardButton(text=city, callback_data=uri))
            markup.row(*city_buttons)

        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=markup)

        text_out = "Можно нажать на кнопочку, и предложить добавить еще какой-нибудь город )"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Написать администратору", callback_data=create_uri('/bla_bla_bla'))
        )

        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=markup)


    def handle_save_city(self, call):
        call_data = call.data
        query_dict = get_query_dict(call_data)
        city = query_dict.get('city')
        if not CityEnum.is_this_city_exist(city):
            logger.error('Неизвестный город: %s' % city)
            return


        buyer = Buyer.objects.get(telegram_user_id=self.chat_id)
        buyer.city = city
        buyer.save()

        text_out = u'Отлично, выбран "%s". Я запомнил и буду показывать погоду для этого города' % city
        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.menu_markup)




    def handle_send_message_to_administator_preview_back(self, message):
        text_out = u'Возврат в начало'
        self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)

    def handle_send_message_to_administator_preview(self, message):
        text_out = u'Задайте вопрос администратору:'
        is_started = self._start_question_dialog(message)
        if is_started:
            self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.close_product_dialog_markup)

    # def handle_need_phone(self, message):
    #     matched_result = re.search(u'[^\+\s\(\)\d]+', message.text)
    #     if matched_result:
    #         self.pseudo_session.set(CacheKey.NEED_PHONE, True)
    #         text_out = u'Так не пойдет, нужно ввести ваш номер телефона в формате "код_страны код_оператора телефон". Пример: 7 495 1234567 %s' % Smile.SMILING_FACE_WITH_SMILING_EYE
    #         self.shop_telebot.send_message(message.chat.id, text_out)
    #     else:
    #         phone_number = message.text
    #         product_id = self.pseudo_session.get(CacheKey.PRODUCT_ID)
    #         product = Product.objects.get(id=product_id)
    #         buyer = Buyer.objects.filter(telegram_user_id=self.chat_id).get()
    #         buyer.phone = phone_number
    #         buyer.save()
    #         order = Order.objects.create(buyer=buyer, product=product)
    #         info_text = u'Заказ id=%s создан' % order.id
    #         logger.info(info_text)
    #         text_out = u'Спасибо, ваши контакты (%s) были отправлены менеджеру компании. Ожидайте он свяжется с вами' % phone_number
    #         self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)
    #
    #         send_mail_to_the_shop(order)
    #
    # def handle_send_message_to_administator(self, message):
    #     self._core_question_to_bot_support(message)
    #
    #
    # def handle_default(self, message):
    #     # дефолтный хэдлер, если не нашло подходящий
    #     text_out = u'Команда "%s" не найдена, попробуйте выбрать другую команду' % message.text
    #     self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)
    #     buyer = Buyer.objects.filter(telegram_user_id=self.chat_id).get()
    #     MessageLog.objects.create(message_text=message.text, bot_id=self.bot_id, buyer=buyer)
    #
    #
    # def handle_answer_from_bot_support(self, message):
    #     self._core_answer_from_bot_support(message)
    #
    def handle_question_to_bot_support(self, message):
        self._core_question_to_bot_support(message)
    #
    # def handle_start_question_about_product(self, call):
    #     call_data = call.data
    #     query_dict = get_query_dict(call_data)
    #     product_id = int(query_dict.get('product_id'))
    #     text_out = u'Товар N. Задайте вопрос по товару N'
    #
    #     self._start_question_dialog(product_id)
    #
    #     self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.close_product_dialog_markup)
    #
    # def handle_close_question_dialog(self, message):
    #     self._close_question_dialog()
    #

    def _start_question_dialog(self, message):
        if message.chat.id == self.bot_support_chat_id:
            text_out = u'Хозяин, ты администратор, зачем ты хочешь отправить сообщение сам себе?'
            self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.menu_markup)
            return False
        key_value = CacheKeyValue().QUESTION_MODE
        # if product_id:
        #     key_value.data.update(product_id=product_id)
        self.pseudo_session.set(key_value.get_cache_key(), key_value.data)
        return True

    def _close_question_dialog(self):
        self.pseudo_session.delete(CacheKeyValue().QUESTION_MODE.get_cache_key())
        text_out = u'Разговор закончен. Спасибо.'
        self.shop_telebot.send_message(self.chat_id, text_out, reply_markup=self.menu_markup)

    def _core_question_to_bot_support(self, message):
        # логика с отправкой email
        #
        # if not self.bot_support_chat_id:
        #     pass
        #     text_out = u'К сожалению к данному боту не подключен оператор поддержки клиентов ((.\n' \
        #            u'Поэтому ваше сообщение оправлено администратору по email. Ответ в течение 1-48 часов'
        #
        #     buyer = Buyer.objects.filter(telegram_user_id=message.chat.id).get()
        #     #Feedback.objects.create(bot_id=self.bot_id, description=message.text, buyer=buyer)
        #     user_contacts = u'%s %s, %s' % (buyer.first_name, buyer.last_name, buyer.phone)
        #     mail_text = u'Сообщение: %s\n От кого: %s' % (message.text, user_contacts)
        #
        #     # todo: вынести отправку письма в celery, добавить кнопку с телефоном, если он не заполнен
        #     result = send_mail(u'От бота артбелки', mail_text, settings.EMAIL_FULL_ADDRESS, [settings.EMAIL_SHOP_BOT_ADMIN])
        #
        #     self.shop_telebot.send_message(message.chat.id, text_out, reply_markup=self.menu_markup)
        #     logger.warning(u'Не установлен оператор поддержки для бота id=%s' % self.bot_id)
        #
        #     self.pseudo_session.delete(CacheKeyValue().QUESTION_MODE.get_cache_key())
        #
        #     return

        markup = types.ForceReply()
        text_out = u'Пользователь: %s %s (id=%s) Спрашивает:\n%s' % (message.chat.first_name, message.chat.last_name, message.chat.id, message.text)
        self.shop_telebot.send_message(self.bot_support_chat_id, text=text_out, reply_markup=markup)
        BotBuyerMap.objects.filter(bot_id=self.bot_id, buyer__telegram_user_id=message.chat.id).update(dialog_with_support=Concat(F('dialog_with_support'),Value(u'%s\n' % text_out)))

        key_value = CacheKeyValue().QUESTION_MODE
        key_value_cached = self.pseudo_session.get(key_value.get_cache_key(), {})
        logger.info(self.chat_id)
        if not key_value_cached.get('is_buyer_notified'):
            self.shop_telebot.send_message(self.chat_id, text=u'*Bot*: Я передал сообщение администратору. Я передам все что напишите до нажатия на "Закончить разговор" ', parse_mode='markdown')
            key_value.data['is_buyer_notified'] = True
            self.pseudo_session.set(key_value.get_cache_key(), key_value.data)

    def _core_answer_from_bot_support(self, message):
        buyer_chat_id = re.search(TsdRegExp.FIND_USER_IN_REPLY, message.reply_to_message.text).group(1)

        # введем пользователя в режим диалога с администратором если этот режим был закрыт
        key_value = CacheKeyValue().QUESTION_MODE
        if not self.pseudo_session.get(key_value.get_cache_key(), chat_id=buyer_chat_id):
            key_value.data.update(is_buyer_notified=True)
            self.pseudo_session.set(key_value.get_cache_key(), key_value.data, chat_id=buyer_chat_id)

        text_out = u'*Администратор*: %s' % message.text
        try:
            self.shop_telebot.send_message(buyer_chat_id, text=text_out, reply_markup=self.close_product_dialog_markup, parse_mode='markdown')
            BotBuyerMap.objects.filter(bot_id=self.bot_id, buyer__telegram_user_id=buyer_chat_id).update(dialog_with_support=Concat(F('dialog_with_support'), Value(u'%s\n' % text_out)))
        except apihelper.ApiException as e:
            error_msg = 'Forbidden: bot was blocked by the user'
            if e.result.status_code == 403 and error_msg in e.result.text:
                buyer = Buyer.objects.filter(telegram_user_id=buyer_chat_id).get()
                text_out = u'Пользователь %s (id=%s) заблокировал бота' % (buyer.full_name, buyer_chat_id)
                self.shop_telebot.send_message(self.bot_support_chat_id, text=text_out)
    #
    # def _core_get_product_description(self):
    #     pass


