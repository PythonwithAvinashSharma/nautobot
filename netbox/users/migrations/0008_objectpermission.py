from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0007_proxy_group_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('enabled', models.BooleanField(default=True)),
                ('constraints', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('actions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=None)),
                ('object_types', models.ManyToManyField(limit_choices_to={'app_label__in': ['circuits', 'dcim', 'extras', 'ipam', 'secrets', 'tenancy', 'virtualization']}, related_name='object_permissions', to='contenttypes.ContentType')),
                ('groups', models.ManyToManyField(blank=True, related_name='object_permissions', to='auth.Group')),
                ('users', models.ManyToManyField(blank=True, related_name='object_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Permission',
            },
        ),
    ]
