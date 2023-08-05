# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('confirmationid', models.CharField(unique=True, max_length=255, verbose_name='Confirmation id')),
                ('confirmed', models.BooleanField(default=False, verbose_name='Confirmed')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('confirm_success_template', models.CharField(max_length=200, verbose_name='Template that shows the user a success message on confirmation', blank=True)),
                ('confirm_success_url', models.CharField(max_length=200, verbose_name='Redirect the user to this url when the url is confirmed', blank=True)),
                ('toconfirm_id', models.PositiveIntegerField()),
                ('toconfirm_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
