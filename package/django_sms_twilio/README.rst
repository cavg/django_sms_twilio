======
sms_twilio
=====

sms_twilio is a simple Django app.

Detailed documentation is in the 'docs' directory.

Quick start
-----------

1. Add 'sms_twilio' to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'sms_twilio',
    ]

2. Include the sms_twilio URLconf in your project urls.py like this::

    url(r'^sms_twilio/', include('sms_twilio.urls')),

3. Run  to create the sms_twilio models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a poll (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/sms_twilio/.
