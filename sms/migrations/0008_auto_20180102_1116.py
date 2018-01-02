# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-02 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0007_auto_20180102_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms',
            name='error_code',
            field=models.IntegerField(blank=True, choices=[(1, 'Error en datos de reemplazos'), (2, 'Error en valores de reemplazos'), (3, 'Error en valores de reemplazos y datos'), (4, 'Error servicio de envió de sms'), (5, 'Error el texto no puede superar los 1600 caracteres')], default=None, null=True),
        ),
    ]