# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib import admin

from weather_bot_app.models import Buyer, Bot, BotBuyerMap, MessageLog


class GetBotMixin(object):
    def get_bot(self, request):
        # выделено в отдельный метод, т.к. мы работаем с одним пользователем на бота, а в будущем пока не понятно
        bot = Bot.objects.filter(administrator=request.user).get()
        return bot


class CustomModelAdmin(admin.ModelAdmin, GetBotMixin):
    exclude = ['bot']

    def save_model(self, request, obj, form, change):
        obj.bot = self.get_bot(request)
        return super(CustomModelAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(CustomModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs

        bot = self.get_bot(request)
        return qs.filter(bot=bot)


class BuyerAdmin(admin.ModelAdmin):
    pass


class BotAdministratorProfileAdmin(admin.ModelAdmin):
    pass


class BotAdminForm(forms.ModelForm):
    hello_description = forms.CharField(widget=forms.Textarea, help_text='Начальное описание после /start')

    class Meta:
        model = Bot
        fields = ['name', 'telegram_token', 'order_email', 'hello_description', 'bot_support']


class BotAdmin(admin.ModelAdmin):
    form = BotAdminForm
    readonly_fields = ['administrator']

    def get_queryset(self, request):
        qs = super(BotAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(administrator=request.user)


class BotBuyerMapAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_blocked_by_user', 'dialog_with_support']


class MessageLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_text', 'created_at', 'buyer', 'bot']


admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Bot, BotAdmin)
admin.site.register(BotBuyerMap, BotBuyerMapAdmin)
admin.site.register(MessageLog, MessageLogAdmin)
