from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from twilio.rest import Client

import datetime


class ConfigSMS(models.Model):
    max_month =  models.IntegerField(blank=False, null=False, default = settings.DEFAULT_SMS_LIMIT_BY_DAY) # Negative value means no limit
    max_day =  models.IntegerField(blank=False, null=False, default = settings.DEFAULT_SMS_LIMIT_BY_MONTH) # Negative value means no limit
    account_sid = models.CharField(max_length=50, blank=False, null=False, default=settings.TWILIO_ACCOUNT_SID)
    account_token = models.CharField(max_length=50, blank=False, null=False, default=settings.TWILIO_AUTH_TOKEN)
    default_number = models.CharField(max_length=20, blank=False, null=False, default=settings.TWILIO_NUMBER)

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
    body = models.CharField(max_length=255, blank=False, null=False)
    number_from = models.CharField(max_length=15, blank=False, null=False)
    number_to = models.CharField(max_length=15, blank=False, null=False)
    status = models.CharField(max_length=500, blank=True, null=False)
    sid = models.CharField(max_length=50, blank=True, null=False)

    config = models.ForeignKey(ConfigSMS, on_delete=models.CASCADE, blank=False, null=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "SMS: {}, TO:{}, STATUS:{}".format(self.body, self.number_to, self.status)

    def _check_quota(self):
        if self.config.is_unlimited():
            return True, None
        else:
            dt = datetime.datetime.now()
            count_by_day = SMS.objects.filter(config=self.config, created_at__year=dt.year, created_at__month=dt.month, created_at__day=dt.day).count()
            count_by_month = SMS.objects.filter(config=self.config, created_at__year=dt.year, created_at__month=dt.month).count()
            msg = "El usuario ha llegado a su máximo de SMS diarios ({}) y/o mensuales ({})".format(self.config.max_day, self.config.max_month)

            if count_by_day <= self.config.max_day:
                if count_by_month <= self.config.max_month:
                    return True, None
                else:
                    return False, msg
            else:
                return False, msg

    def send(self):
        if settings.ENABLE_SMS:
            with_quotes, detail = self._check_quota()
            if with_quotes:
                client = Client(self.config.account_sid, self.config.account_token)
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


