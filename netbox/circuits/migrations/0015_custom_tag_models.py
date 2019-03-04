# Generated by Django 2.1.4 on 2019-02-20 06:56

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0014_circuittermination_description'),
        ('extras', '0017_tag_taggeditem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circuit',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
