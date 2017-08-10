Django APP that provide an integration with twilio SMS service.

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

    url(r'^sms_twilio/', include('sms_twilio.urls')),

    INSTALLED_APPS = [
        ...
        'sms_twilio',
    ]

## Notes:

In debug mode, SMS are not sent using twilio to avoid charges.



# Install instructions

`pip3 install -r package/django_sms_twilio/requirements.txt`

`sh install.sh`