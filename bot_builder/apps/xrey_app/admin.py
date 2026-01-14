from django.contrib import admin
from .models import VPNServer


@admin.register(VPNServer)
class VPNServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'xui_host', 'count_user', 'xui_external_ip', 'main_remark',  'port_client', 'inbound_id')
    list_filter = ('port_client',)
    search_fields = ('xui_host', 'xui_external_ip', 'main_remark')
    fieldsets = (
        ('Данные сервера', {
            'fields': ('count_user', 'xui_host', 'xui_external_ip', 'main_remark')
        }),
        ('Учетные данные', {
            'fields': ('xui_username', 'xui_password')
        }),
        ('Технические параметры', {
            'fields': ('port_client', 'inbound_id')
        }),
    )
