# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_rpy2', '0002_scriptresult_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='availablelibrary',
            name='location',
            field=models.CharField(default=b'unknown', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='availablelibrary',
            name='name',
            field=models.CharField(max_length=32),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='availablelibrary',
            unique_together=set([('name', 'location')]),
        ),
    ]
