# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-19 16:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estore', '0015_remove_order_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]