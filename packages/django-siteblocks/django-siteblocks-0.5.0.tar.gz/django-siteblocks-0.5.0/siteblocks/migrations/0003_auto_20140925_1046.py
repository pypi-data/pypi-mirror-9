# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('siteblocks', '0002_auto_20140921_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='block',
            name='access_guest',
            field=models.BooleanField(default=False, help_text='Check it to grant access to this block to guests only.', db_index=True, verbose_name='Guests only'),
        ),
        migrations.AlterField(
            model_name='block',
            name='access_loggedin',
            field=models.BooleanField(default=False, help_text='Check it to grant access to this block to authenticated users only.', db_index=True, verbose_name='Logged in only'),
        ),
    ]
