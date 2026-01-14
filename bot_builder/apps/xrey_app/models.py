from django.db import models


class VPNServer(models.Model):
    count_user = models.IntegerField(help_text='Сколько пользоватлей на сервере?', default=0)
    xui_host = models.CharField(max_length=500,help_text='hsot', null=True, blank=True)
    xui_username = models.CharField(max_length=500,help_text='xui_username', null=True, blank=True)
    xui_password = models.CharField(max_length=500,help_text='xui_password', null=True, blank=True)
    xui_external_ip = models.CharField(max_length=500,help_text='xui_external_ip', null=True, blank=True)
    main_remark = models.CharField(max_length=500,help_text='main_remark', default='W%20VPN')
    port_client = models.IntegerField(help_text='port_client', default=443)
    inbound_id = models.IntegerField(help_text='inbound_id', default=1)

    def __str__(self):
        return f"Server {self.xui_host}"
