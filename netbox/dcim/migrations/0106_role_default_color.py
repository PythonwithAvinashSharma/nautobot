# Generated by Django 3.0.6 on 2020-05-26 13:33

from django.db import migrations
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0105_interface_name_collation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicerole',
            name='color',
            field=utilities.fields.ColorField(default='9e9e9e', max_length=6),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='color',
            field=utilities.fields.ColorField(default='9e9e9e', max_length=6),
        ),
    ]
