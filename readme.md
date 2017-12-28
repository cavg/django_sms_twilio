Django APP that provide an integration with twilio SMS service.

Tested on Django 1.11.2 and Python 3.6.1 \o/

# Features

* SMS sender through Twilio API
* Callback status update for deliverd sms
* Quote by user monthly and daily
* SID, Token twilio storaged in DB


# Setup

## Environment vars required

    TWILIO_NUMBER
    TWILIO_TEST_NUMBER_TO
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN


## Required settings

    TWILIO_NUMBER
    TWILIO_TEST_NUMBER_TO
    TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN

    ENABLE_SMS = False
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

#### 0.0.4
* Rename model from Quota to ConfigSMS
* New feature: Save SID, TOKEN into DB
* Associate SMS with config to get credentials and limits

# Dependencies

`pipenv install`