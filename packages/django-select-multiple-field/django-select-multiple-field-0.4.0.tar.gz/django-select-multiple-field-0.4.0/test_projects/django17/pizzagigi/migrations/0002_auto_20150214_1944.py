# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import select_multiple_field.models


class Migration(migrations.Migration):

    dependencies = [
        ('pizzagigi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pizza',
            name='dips',
            field=select_multiple_field.models.SelectMultipleField(default='', include_blank=False, choices=[('r', 'Ranch'), ('h', 'Honey mustard'), ('b', 'BBQ')], max_choices=3, max_length=6, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pizza',
            name='toppings',
            field=select_multiple_field.models.SelectMultipleField(max_length=10, choices=[('a', 'Anchovies'), ('b', 'Black olives'), ('c', 'Cheddar cheese'), ('e', 'Eggs'), ('pk', 'Pancetta'), ('p', 'Pepperoni'), ('P', 'Prosciutto crudo'), ('m', 'Mozzarella'), ('M', 'Mushrooms'), ('t', 'Tomato')]),
            preserve_default=True,
        ),
    ]
