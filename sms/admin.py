# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import SMS, ConfigSMS

class SMSAdmin(admin.ModelAdmin):
    list_display = ("sender", "body", "number_from", "number_to", "status", "created_at", "updated_at")

admin.site.register(SMS, SMSAdmin)


class ConfigSMSAdmin(admin.ModelAdmin):
    list_display = ("user", "max_month", "max_day", "created_at")

admin.site.register(ConfigSMS, ConfigSMSAdmin)
