from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User

from .models import ConfigSMS, SMS

class ConfigSMSTestCase(TestCase):

    def setUp(self):
        pass

    def test_automatic_create_config_sms(self):
        config_sms = ConfigSMS.objects.filter().count()
        self.assertEqual(config_sms,0)

        user = User.objects.create(
            first_name = "User1322",
            last_name = "Recolector",
            email = "agent@empresa.cl",
            username = "agent@empresa.cl"
        )

        config_sms = ConfigSMS.objects.get(user=user)
        self.assertEqual(config_sms.user,user)
        self.assertEqual(config_sms.max_month, settings.DEFAULT_SMS_LIMIT_BY_MONTH)
        self.assertEqual(config_sms.max_day, settings.DEFAULT_SMS_LIMIT_BY_DAY)

        config_sms.set_no_limit()
        self.assertEqual(config_sms.max_month, -1)
        self.assertEqual(config_sms.max_day, -1)
        self.assertEqual(config_sms.is_unlimited(), True)


class SMSTestCase(TestCase):

    def setUp(self):
        pass

    def test_check_quota(self):
        user = User.objects.create(
            first_name = "User1322",
            last_name = "Recolector",
            email = "agent@empresa.cl",
            username = "agent@empresa.cl"
        )
        config_sms = ConfigSMS.objects.get(user=user)

        # Testing user sms disabled (no exist ConfigSMS)
        config_sms.delete()
        sms = SMS.objects.create(
            body = "msg",
            number_to = "+569234234",
            sender = user
        )
        status, msg = sms._check_quota()
        self.assertEqual(status, False)
        self.assertEqual(msg, "El usuario no está habilitado para enviar SMS")

        # Testing user without limit
        config_sms = ConfigSMS.objects.create(
            user = user
        )
        config_sms.set_no_limit()
        status, msg = sms._check_quota()
        self.assertEqual(status, True)
        self.assertEqual(msg, None)
        self.assertEqual(config_sms.is_unlimited(), True)

        # Testing user below limit
        self.assertEqual(SMS.objects.filter(sender=user).count(), 1)
        config_sms.max_day = 1
        config_sms.max_month = 2
        config_sms.save()
        self.assertEqual(config_sms.is_unlimited(), False)
        status, msg = sms._check_quota()
        self.assertEqual(status, True)
        self.assertEqual(msg, None)

        # Testing user reach limit by day
        self.assertEqual(config_sms.max_day, 1)
        SMS.objects.create(
            body = "msg",
            number_to = "+569234234",
            sender = user
        )
        self.assertEqual(SMS.objects.filter(sender=user).count(), 2)
        status, msg = sms._check_quota()
        self.assertEqual(status, False)
        self.assertEqual(msg, "El usuario ha llegado a su máximo de SMS diarios ({}) y/o mensuales ({})".format(config_sms.max_day, config_sms.max_month))

    def test_send(self):
        user = User.objects.create(
            first_name = "User1322",
            last_name = "Recolector",
            email = "agent@empresa.cl",
            username = "agent@empresa.cl"
        )

        if settings.DETAULT_SMS_TEST_NUMBER is not None:
            sms = SMS.objects.create(
                body = "msg",
                number_to = settings.DETAULT_SMS_TEST_NUMBER,
                sender = user
            )

            # Testing delivery disabled by setting
            with self.settings(ENABLE_SMS=False):
                status, msg = sms.send()
                self.assertEqual(sms.status, 'disable_sms')
                self.assertEqual(status, False)
                self.assertEqual(msg, "Delivery disabled by setting.ENABLE_SMS flag")

            # Testing send
            config_sms = ConfigSMS.objects.get(user=user)
            config_sms.set_no_limit()
            with self.settings(ENABLE_SMS=True):
                with self.settings(DEBUG=True):
                    status, msg = sms.send()
                    self.assertEqual(sms.status, 'queued')
                    self.assertIsNotNone(sms.sid)
                    self.assertEqual(status, True)






