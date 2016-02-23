# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exception', models.CharField(max_length=64, null=True, blank=True)),
                ('traceback', models.TextField(max_length=1024, null=True, blank=True)),
                ('traceback_msg', models.TextField(null=True, blank=True)),
                ('params', models.TextField(null=True, blank=True)),
                ('vars', models.TextField(null=True, blank=True)),
                ('status', models.CharField(max_length=16, null=True, blank=True)),
                ('received', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(default=b'User', max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.CharField(max_length=512)),
                ('code_obj_name', models.CharField(max_length=128)),
                ('max_errors', models.IntegerField(default=25)),
            ],
        ),
        migrations.CreateModel(
            name='Rescue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('error_tb_pattern', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=20)),
                ('max_retries', models.IntegerField(default=0)),
                ('priority', models.IntegerField(default=1)),
                ('destination', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('delay', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Retry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('result', models.CharField(max_length=20)),
                ('attempted', models.DateTimeField(auto_now_add=True)),
                ('error', models.ForeignKey(to='lifeboat.Error')),
                ('rescue', models.ForeignKey(to='lifeboat.Rescue')),
            ],
        ),
        migrations.CreateModel(
            name='Statistic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(max_length=20)),
                ('date_format', models.CharField(max_length=50)),
                ('stat_regex', models.CharField(max_length=200)),
                ('match_regex', models.CharField(max_length=200)),
                ('path', models.CharField(max_length=200)),
                ('value', models.BigIntegerField(default=0)),
                ('last_read', models.DateTimeField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='error',
            name='module',
            field=models.ForeignKey(to='lifeboat.Module'),
        ),
    ]
