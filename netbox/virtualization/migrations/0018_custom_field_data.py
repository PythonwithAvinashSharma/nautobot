# Generated by Django 3.1 on 2020-08-21 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0017_update_jsonfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
