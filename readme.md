Django APP that provide an integration with twilio SMS service.

Tested on Django 1.11.2 and Python 3.6.1 \o/

# Features

* SMS sender through Twilio API
* Callback status update for deliverd sms
* Quote by user monthly and daily


# Setup

## Environment vars required

    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN
    TWILIO_NUMBER
    TWILIO_TEST_TO_NUMBER

## Required settings

DEFAULT_SMS_LIMIT_BY_DAY = 2
DEFAULT_SMS_LIMIT_BY_MONTH = 2
SITE_URL = "."...


## URL and settings

    url(r'^sms/', include('sms.urls')),

    INSTALLED_APPS = [
        ...
        'sms.apps.SmsConfig',
    ]

## Notes:

In debug mode, SMS are not sent using twilio to avoid charges.


## Changelog

#### 0.0.3
* to delivery use sms.send() will check the quote limit automatically
* method check_quota was deprecated
* unlimit quote is valid if max_day or max_month are negative

# Dependencies

`pipenv install`