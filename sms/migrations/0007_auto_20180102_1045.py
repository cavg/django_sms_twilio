# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-02 13:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0006_auto_20171229_1045'),
    ]

    operations = [
        migrations.AddField(
            model_name='sms',
            name='deliver_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='sms',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
