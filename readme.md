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


## URL and settings

    url(r'^sms/', include('sms.urls')),

    INSTALLED_APPS = [
        ...
        'sms.apps.SmsConfig',
    ]

## Notes:

In debug mode, SMS are not sent using twilio to avoid charges.



# Install instructions

`pip3 install -r package/django_sms_twilio/requirements.txt`

`sh install.sh`