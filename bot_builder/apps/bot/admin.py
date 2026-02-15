# Register your models here.
from django.contrib import admin
from .models import *
from django.contrib import admin
import csv
from django.http import HttpResponse
from django import forms
from django.contrib.admin.widgets import AdminRadioSelect


@admin.register(Bot_Button)
class Bot_ButtonAdmin(admin.ModelAdmin):
    fields = [
        "text",
        "message_trigger",
        "type_data",
        "data",
        "type_btn",
        "button_position",
        
    ]
    list_display = (
        "text",
        "message_trigger",
        "type_data",
        "type_btn",
    )
    list_filter = (
        "text",
        "message_trigger",
        "type_data",
        "type_btn",
    )
    search_fields = (
        "text",
        "message_trigger",
        "type_data",
        "type_btn",
    )


@admin.register(TelegramBotConfig)
class TelegramBotConfigAdmin(admin.ModelAdmin):

    fields = [
        "bot_token",
        "is_activ",
    ]
    list_display = (
        "bot_token",
        "is_activ",
    )
    list_filter = (
        "is_activ",
    )
    search_fields = (
        "bot_token",
    )

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    fields = [
        "tg_id",
        "first_name",
        "last_name",
        "username",
        "language",
        "language_chooce",
        "premium",
        "state",
        "referal_url",
        "server_chooce",

        "subscription",
        "trial_period",
        "subscription_date_start",
        "subscription_date_end",

        "key_id",
        "vpn_key",
        "name_key",

        "last_message_id",  # Оставлено только одно упоминание
        "last_input_message_id",

    ]
    list_display = (
        "tg_id",
        "first_name",
        "username",
        "server_chooce",
        "state",
        "subscription_date_start",
        "subscription_date_end",
    )
    list_filter = (
        "server_chooce",
        "subscription",
        "trial_period",
    )
    search_fields = (
        "tg_id",
        "username",
        "id"
    )

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=botusers.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        return response

    export_as_csv.short_description = "Экспортировать выбранные в CSV"

class Bot_ButtonStackedInline(admin.StackedInline):
    model = Bot_Button
    extra = 1
    fields = (
        ('text', 'type_data', 'data', 'type_btn', 'button_position'),
    )

@admin.register(Bot_Message)
class Bot_MessageAdmin(admin.ModelAdmin):
    inlines = [Bot_ButtonStackedInline]
    fields = [
        "text",
        "current_state",
        "next_state",
        "anyway_link",
        "handler",

    ]
    list_display = (
        "text", 
        "current_state",
        "next_state",
        "handler",
    )
    list_filter = (
        "handler",
    )
    search_fields = (
        "handler",
    )

@admin.register(Bot_Commands)
class Bot_CommandsAdmin(admin.ModelAdmin):
    fields = [
        "text",
        "trigger",
    ]
    list_display = (
        "text",
        "trigger",
    )
    list_filter = (
        "text",
        "trigger",
    )
    search_fields = (
        "text",
        "trigger",
    )

@admin.register(Referal)
class ReferalAdmin(admin.ModelAdmin):

    readonly_fields = ("created_at",)

    fields = [
        "user",
        "referred_user",
        "created_at"
    ]
    list_display = (
        "user__tg_id",
        "referred_user__tg_id",
        "created_at"
    )
    list_filter = (
        "created_at",
    )
    search_fields = (
        "user__tg_id",
        "referred_user__tg_id",
    )

@admin.register(PaymentReferal)
class PaymentReferalAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at",)

    fields = [
        "referal",
        "amount",
        "created_at",
    ]
    list_display = (
        "referal",
        "amount",
        "created_at",
    )
    list_filter = (
        "created_at",
    )
    search_fields = (
        "referal_user__tg_id",
    )

@admin.register(Text_Castom)
class Text_CastomsAdmin(admin.ModelAdmin):
    fields = [
        "condition",
        "hint",
        "text",
    ]
    list_display = (
        "condition",
        "hint",
    )
    list_filter = (
        "condition",
    )
    search_fields = (
        "condition",
        "hint",
    )

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    fields = [
        "payment_id",
        "user_id",
        "limit_ip",
        "period",
        "status",
        "value",
        "created_at",
    ]
    list_display = (
        "payment_id",
        "user_id",
        "limit_ip",
        "period",
        "status",
        "value",
        "created_at",
    )
    list_filter = (
        # "payment_id",
        "period",
        "limit_ip",
        "status",
    )
    search_fields = (
        "user_id",
        "payment_id",
        "period",
        "limit_ip",
        "status",
    )


