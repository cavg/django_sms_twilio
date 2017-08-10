# pip3 uninstall -y django_sms_twilio &&

# Packing new version
cd package/django_sms_twilio/ &&
python3 setup.py sdist &&

#Install new version
pip3 install --user dist/django_sms_twilio-0.0.1.tar.gz &&
cd ../../
