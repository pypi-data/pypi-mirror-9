# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=32)),
                ('version', models.CharField(max_length=12, null=True, blank=True)),
                ('installed', models.DateTimeField(null=True, blank=True)),
                ('attempted', models.DateTimeField(null=True, blank=True)),
                ('scheduled', models.BooleanField(default=True, verbose_name=b'Schedule Install')),
            ],
            options={
                'verbose_name_plural': 'Available Libraries',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScriptResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField(null=True, blank=True)),
                ('ended', models.DateTimeField(null=True, blank=True)),
                ('fn_out', models.FileField(upload_to=b'rpy/out/', null=True, verbose_name=b'File Output', blank=True)),
                ('output', models.TextField(null=True, verbose_name=b'Printed to Screen', blank=True)),
                ('result', models.TextField(null=True, verbose_name=b'Result or Error', blank=True)),
            ],
            options={
                'ordering': ('-started',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UploadedScript',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('slug', models.SlugField(max_length=64)),
                ('db', models.CharField(blank=True, max_length=32, null=True, verbose_name=b'Database', choices=[(b'default', b'default')])),
                ('rsc', models.TextField(help_text=b"Use data sources:\n\n      Uploaded CSV Data is available as 'csv'\n      Website databases available as 'default' or name of database.\n      Output filename is 'filename'.\n    ", verbose_name=b'R Script')),
                ('csv', models.FileField(upload_to=b'rpy/csv/', null=True, verbose_name=b'CSV Data', blank=True)),
                ('libs', models.ManyToManyField(to='django_rpy2.AvailableLibrary', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='scriptresult',
            name='script',
            field=models.ForeignKey(related_name='results', to='django_rpy2.UploadedScript'),
            preserve_default=True,
        ),
    ]
