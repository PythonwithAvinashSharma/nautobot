# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-31 02:19
import re
from distutils.version import StrictVersion

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import connection, migrations, models
import django.db.models.deletion
import extras.models
from django.db.utils import OperationalError

from extras.constants import CF_FILTER_DISABLED, CF_FILTER_EXACT, CF_FILTER_LOOSE, CF_TYPE_SELECT


def verify_postgresql_version(apps, schema_editor):
    """
    Verify that PostgreSQL is version 9.4 or higher.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            row = cursor.fetchone()
            pg_version = re.match(r'^PostgreSQL (\d+\.\d+(\.\d+)?)', row[0]).group(1)
            if StrictVersion(pg_version) < StrictVersion('9.4.0'):
                raise Exception("PostgreSQL 9.4.0 or higher is required ({} found). Upgrade PostgreSQL and then run migrations again.".format(pg_version))

    # Skip if the database is missing (e.g. for CI testing) or misconfigured.
    except OperationalError:
        pass


class Migration(migrations.Migration):

    replaces = [('extras', '0001_initial'), ('extras', '0002_custom_fields'), ('extras', '0003_exporttemplate_add_description'), ('extras', '0004_topologymap_change_comma_to_semicolon'), ('extras', '0005_useraction_add_bulk_create'), ('extras', '0006_add_imageattachments'), ('extras', '0007_unicode_literals'), ('extras', '0008_reports'), ('extras', '0009_topologymap_type'), ('extras', '0010_customfield_filter_logic')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dcim', '0002_auto_20160622_1821'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('template_code', models.TextField()),
                ('mime_type', models.CharField(blank=True, max_length=15)),
                ('file_extension', models.CharField(blank=True, max_length=15)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['content_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(100, 'Interface'), (200, 'Provider'), (300, 'Site')])),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('source', models.CharField(max_length=500, verbose_name='Source URL')),
                ('link', models.URLField(blank=True, verbose_name='Link URL')),
            ],
            options={
                'ordering': ['type', 'weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='TopologyMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('device_patterns', models.TextField(help_text='Identify devices to include in the diagram using regular expressions, one per line. Each line will result in a new tier of the drawing. Separate multiple regexes within a line using semicolons. Devices will be rendered in the order they are defined.')),
                ('description', models.CharField(blank=True, max_length=100)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='topology_maps', to='dcim.Site')),
                ('type', models.PositiveSmallIntegerField(choices=[(1, 'Network'), (2, 'Console'), (3, 'Power')], default=1)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'created'), (7, 'bulk created'), (2, 'imported'), (3, 'modified'), (4, 'bulk edited'), (5, 'deleted'), (6, 'bulk deleted')])),
                ('message', models.TextField(blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='exporttemplate',
            unique_together=set([('content_type', 'name')]),
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(100, 'Text'), (200, 'Integer'), (300, 'Boolean (true/false)'), (400, 'Date'), (500, 'URL'), (600, 'Selection')], default=100)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('label', models.CharField(blank=True, help_text="Name of the field as displayed to users (if not provided, the field's name will be used)", max_length=50)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('required', models.BooleanField(default=False, help_text='If true, this field is required when creating new objects or editing an existing object.')),
                ('default', models.CharField(blank=True, help_text='Default value for the field. Use "true" or "false" for booleans.', max_length=100)),
                ('weight', models.PositiveSmallIntegerField(default=100, help_text='Fields with higher weights appear lower in a form.')),
                ('obj_type', models.ManyToManyField(help_text='The object(s) to which this field applies.', related_name='custom_fields', to='contenttypes.ContentType', verbose_name='Object(s)')),
                ('filter_logic', models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Loose'), (2, 'Exact')], default=1, help_text='Loose matches any instance of a given string; exact matches the entire field.')),
            ],
            options={
                'ordering': ['weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomFieldChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('weight', models.PositiveSmallIntegerField(default=100, help_text='Higher weights appear lower in the list')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='extras.CustomField')),
            ],
            options={
                'ordering': ['field', 'weight', 'value'],
            },
        ),
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obj_id', models.PositiveIntegerField()),
                ('serialized_value', models.CharField(max_length=255)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='extras.CustomField')),
                ('obj_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['obj_type', 'obj_id'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='customfieldvalue',
            unique_together=set([('field', 'obj_type', 'obj_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='customfieldchoice',
            unique_together=set([('field', 'value')]),
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('image', models.ImageField(height_field='image_height', upload_to=extras.models.image_upload, width_field='image_width')),
                ('image_height', models.PositiveSmallIntegerField()),
                ('image_width', models.PositiveSmallIntegerField()),
                ('name', models.CharField(blank=True, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.RunPython(
            code=verify_postgresql_version,
        ),
        migrations.CreateModel(
            name='ReportResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report', models.CharField(max_length=255, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('failed', models.BooleanField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['report'],
            },
        ),
    ]
