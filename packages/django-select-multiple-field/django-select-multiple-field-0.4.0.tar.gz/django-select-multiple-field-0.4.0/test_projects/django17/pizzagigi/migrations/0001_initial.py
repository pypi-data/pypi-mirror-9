# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import select_multiple_field.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Pizza',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('toppings', select_multiple_field.models.SelectMultipleField(max_choices=2, max_length=10, choices=[('a', 'Anchovies'), ('b', 'Black olives'), ('c', 'Cheddar cheese'), ('e', 'Eggs'), ('pk', 'Pancetta'), ('p', 'Pepperoni'), ('P', 'Prosciutto crudo'), ('m', 'Mozzarella'), ('M', 'Mushrooms'), ('t', 'Tomato')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
