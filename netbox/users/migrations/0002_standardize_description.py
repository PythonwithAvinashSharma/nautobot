# Generated by Django 3.0.3 on 2020-03-13 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_api_tokens_squashed_0003_token_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
