# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DBVersion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name / Number')),
                ('json', models.TextField(verbose_name='JSON data')),
                ('date', models.DateField(verbose_name='Created')),
            ],
            options={
                'db_table': 'py_versioning_db_version',
                'verbose_name': 'Database Version',
                'verbose_name_plural': 'Database Versions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FSVersion',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name / Number')),
                ('json', models.TextField(verbose_name='JSON data')),
                ('hash', models.CharField(max_length=255, verbose_name='Hash data')),
                ('date', models.DateField(verbose_name='Created')),
            ],
            options={
                'db_table': 'py_versioning_fs_version',
                'verbose_name': 'File System Version',
                'verbose_name_plural': 'File System Versions',
            },
            bases=(models.Model,),
        ),
    ]
