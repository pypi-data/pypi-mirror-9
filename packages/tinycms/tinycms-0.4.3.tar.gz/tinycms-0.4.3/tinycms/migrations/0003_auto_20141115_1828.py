# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tinycms', '0002_auto_20141030_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='template',
            field=models.CharField(max_length=1024, choices=[(b'test_template.html', b'test_template')]),
        ),
    ]
