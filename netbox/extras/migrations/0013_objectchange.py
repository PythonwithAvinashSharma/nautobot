# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-06-13 20:05
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('extras', '0012_webhooks'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user_name', models.CharField(editable=False, max_length=150)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'Created'), (2, 'Updated'), (3, 'Deleted')])),
                ('object_id', models.PositiveIntegerField()),
                ('object_repr', models.CharField(editable=False, max_length=200)),
                ('object_data', django.contrib.postgres.fields.jsonb.JSONField(editable=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
    ]
