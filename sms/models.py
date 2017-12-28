from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from twilio.rest import Client

import datetime


class ConfigSMS(models.Model):
    max_month =  models.IntegerField(blank=False, null=False, default = settings.DEFAULT_SMS_LIMIT_BY_DAY) # Negative value means no limit
    max_day =  models.IntegerField(blank=False, null=False, default = settings.DEFAULT_SMS_LIMIT_BY_MONTH) # Negative value means no limit

    user = models.OneToOneField(User, on_delete=models.CASCADE) #OneToOneField ensure unique user

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "Username:{} - Day:{} - Month:{}".format(self.user.username, self.max_day, self.max_month)

    def set_no_limit(self):
        self.max_month = -1
        self.max_day = -1
        return self.save()

    def is_unlimited(self):
        return self.max_month < 0 or self.max_day < 0


class SMS(models.Model):
    body = models.CharField(blank=False, max_length=255)
    number_from = models.CharField(blank=False, max_length=15, default=settings.TWILIO_NUMBER)
    number_to = models.CharField(blank=False, max_length=15)
    status = models.CharField(blank=True, max_length=500)
    sid = models.CharField(blank=True, max_length=50)

    sender = models.ForeignKey(User, on_delete=models.CASCADE, default=None, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


    def __str__(self):
        return "SMS: {}, TO:{}, STATUS:{}".format(self.body, self.number_to, self.status)

    def _check_quota(self):
        configSms = ConfigSMS.objects.filter(user=self.sender)
        if (configSms.count() == 0):
            return False, "El usuario no está habilitado para enviar SMS"
        else:
            configSms = configSms.first()
            if configSms.is_unlimited():
                return True, None
            else:
                dt = datetime.datetime.now()
                count_by_day = SMS.objects.filter(sender=self.sender, created_at__year=dt.year, created_at__month=dt.month, created_at__day=dt.day).count()
                count_by_month = SMS.objects.filter(sender=self.sender, created_at__year=dt.year, created_at__month=dt.month).count()
                msg = "El usuario ha llegado a su máximo de SMS diarios ({}) y/o mensuales ({})".format(configSms.max_day, configSms.max_month)

                if count_by_day <= configSms.max_day:
                    if count_by_month <= configSms.max_month:
                        return True, None
                    else:
                        return False, msg
                else:
                    return False, msg

    def send(self):
        if settings.ENABLE_SMS:
            with_quotes, detail = self._check_quota()
            if with_quotes:
                client = Client()
                message = None
                if settings.DEBUG:
                    message = client.messages.create(
                        body = self.body,
                        to = self.number_to,
                        from_ = self.number_from
                    )
                else:
                    message = client.messages.create(
                        body = self.body,
                        to = self.number_to,
                        from_ = self.number_from,
                        status_callback="{}{}".format(settings.SITE_URL,'/sms/callback')
                    )
                self.status = message.status
                self.sid = message.sid
                self.save()
                if self.status == 'queued':
                    return True, None
                else:
                    return False, "Twilio service return: {}".format(self.status)
            else:
                return with_quotes, detail
        else:
            self.status = 'disable_sms'
            self.save()

            return False, "Delivery disabled by setting.ENABLE_SMS flag"


