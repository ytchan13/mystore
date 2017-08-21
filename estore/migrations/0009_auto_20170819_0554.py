# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-19 05:54
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('estore', '0008_remove_cart_items'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart_Items',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=1, verbose_name='數量')),
                ('cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estore.Cart')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='estore.Product')),
            ],
        ),
        migrations.AddField(
            model_name='cart',
            name='items',
            field=models.ManyToManyField(through='estore.Cart_Items', to='estore.Product'),
        ),
    ]
