from django.db import models
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth.models import User
import datetime


class Quota(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    max_month =  models.IntegerField(blank=False, null=False, default = 10)
    max_day =  models.IntegerField(blank=False, null=False, default = 2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return "Username:{} - Day:{} - Month:{}".format(self.user.username, self.max_day, self.max_month)

class SMS(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    body = models.CharField(blank=False, max_length=255)
    number_from = models.CharField(blank=False, max_length=15, default=settings.TWILIO_NUMBER)
    number_to = models.CharField(blank=False, max_length=15)
    status = models.CharField(blank=True, max_length=500)
    sid = models.CharField(blank=True, max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)


    def __str__(self):
        return "SMS: {}, TO:{}, STATUS:{}".format(self.body, self.number_to, self.status)


    def send(self):
        if settings.ENABLE_SMS:
            client = Client()
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
        else:
            self.status = 'disable_sms'
            self.save()
        return True



def send_sms(msg, number_to, user):
    quota = Quota.objects.filter(user__pk=user.pk)
    user = User.objects.get(id=user.pk)
    if (len(quota) == 0):
        return False, "El usuario no está habilitado para enviar SMS"
    else:
        quota = quota[0]
        dt = datetime.datetime.now()
        sms_sent_by_day = SMS.objects.filter(sender=user, created_at__year=dt.year, created_at__month=dt.month, created_at__day=dt.day)
        sms_sent_by_month = SMS.objects.filter(sender=user, created_at__year=dt.year, created_at__month=dt.month)
        if len(sms_sent_by_day) <= quota.max_day and len(sms_sent_by_month) <= quota.max_month:

            sms = SMS()
            sms.sender = user
            sms.body = msg
            sms.number_from = settings.TWILIO_NUMBER
            sms.number_to = number_to
            sms.save()
            return sms.send(), ""
        else:
            return False, "El usuario ha llegado a su máximo de SMS diarios ({}) y/o mensuales ({})".format(quota.max_day, quota.max_month)
