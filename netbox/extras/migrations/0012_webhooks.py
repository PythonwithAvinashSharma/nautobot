# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-23 16:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0011_django2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('type_create', models.BooleanField(default=False, help_text='A POST will be sent to the URL when the object type(s) is created.')),
                ('type_update', models.BooleanField(default=False, help_text='A POST will be sent to the URL when the object type(s) is updated.')),
                ('type_delete', models.BooleanField(default=False, help_text='A POST will be sent to the URL when the object type(s) is deleted.')),
                ('payload_url', models.CharField(max_length=500, verbose_name='A POST will be sent to this URL based on the webhook criteria.')),
                ('http_content_type', models.PositiveSmallIntegerField(choices=[(1, 'application/json'), (2, 'application/x-www-form-urlencoded')], default=1)),
                ('secret', models.CharField(blank=True, help_text="When provided the request will include a 'X-Hook-Signature' header which is a HMAC hex digest of the payload body using the secret as the key. The secret is not transmitted in the request.", max_length=255)),
                ('enabled', models.BooleanField(default=True)),
                ('ssl_verification', models.BooleanField(default=True, help_text='By default, use of proper SSL is verified. Disable with caution!')),
                ('obj_type', models.ManyToManyField(help_text='The object(s) to which this Webhook applies.', related_name='webhooks', to='contenttypes.ContentType', verbose_name='Object(s)')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='webhook',
            unique_together=set([('payload_url', 'type_create', 'type_update', 'type_delete')]),
        ),
    ]
