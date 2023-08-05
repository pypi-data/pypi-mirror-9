# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tinycms', '0001_initial'),
    ]

    operations = [
        #migrations.AlterField(
        #    model_name='content',
        #    name='language',
        #    field=models.CharField(max_length=256, choices=[(b'en', b'English'), (b'ja', b'Japanese')]),
        #),
        migrations.AlterField(
            model_name='page',
            name='url_overwrite',
            field=models.CharField(max_length=2048, null=True, blank=True),
        ),
    ]
