from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

from toolbox.html_parser import MyHTMLParser
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
    ERROR_POPULATE = 1
    ERROR_KEYS = 2
    ERROR_POPULATE_KEYS = 3
    ERROR_SMS = 4
    ERROR_CODE_CHOICES = (
        (ERROR_POPULATE, 'Error en datos de reemplazos'),
        (ERROR_KEYS, 'Error en valores de reemplazos'),
        (ERROR_POPULATE_KEYS, 'Error en valores de reemplazos y datos'),
        (ERROR_SMS, 'Error servicio de envió de sms')
    )
    body = models.TextField(max_length=1600, blank=False, null=False)
    number_from = models.CharField(max_length=15, blank=False, null=False)
    number_to = models.CharField(max_length=15, blank=False, null=False)
    status = models.CharField(max_length=500, blank=True, null=False)
    sid = models.CharField(max_length=50, blank=True, null=False)
    error_code = models.IntegerField(choices=ERROR_CODE_CHOICES, default=None, null=True, blank=True)
    error_detail = models.CharField(max_length=200, blank = True, null = True)

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

    """ Replace template body tags for values an create an instance of Mail
    Args:
        sms_class (Class): Could be parent of SMS
        entity_class (Class): Could be parent of MailTemplateEntity
        extra_filters (array<Q>): using to filter entity_class
        sms_fields (dict): All args required to obtain values to replace in sms body
        populate_values (dict): All args required to obtain values to replace in sms body
        populate_body: (Method) Mail._populate_body
    Returns:
        sms (SMS Instance): - None if not have minimun fields required
                     - SMS instance:
                        - error_code is None then build was successfully
                        - with error_code fail with data to populate, token not founds or both
        not_found_keys (array): not found keys in body
        not_found_args (array): not found replacement params
    """
    @classmethod
    def build(self, sms_class = None, entity_class = None, extra_filters = [] ,sms_fields = {}, populate_values = {}, populate_body_method = None):
        body = None
        nf_keys = []
        nf_args = []
        sms = None

        if len(['body', 'number_from', 'number_to'] -  sms_fields.keys()) == 0:
            body, nf_keys, nf_args = populate_body_method(
                entity_class,
                sms_fields.get('body'),
                extra_filters,
                **populate_values
            )

            parser = MyHTMLParser()
            parser.feed(body)
            sms_fields['body'] = parser.get_plain_text()

            sms = sms_class(
                **sms_fields
            )

            if len(nf_keys) > 0 and len(nf_args) == 0:
                sms.error_code = sms_class.ERROR_KEYS
                sms.error_detail = ",".join(nf_keys)
            if len(nf_args) > 0 and len(nf_keys) == 0:
                sms.error_code = sms_class.ERROR_POPULATE
                sms.error_detail = ",".join(nf_args)
            if len(nf_args) > 0 and len(nf_keys) > 0:
                sms.error_code = sms_class.ERROR_POPULATE_KEYS
                sms.error_detail = ",".join(nf_args+nf_keys)

            sms.save()

        return sms, nf_keys, nf_args

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


