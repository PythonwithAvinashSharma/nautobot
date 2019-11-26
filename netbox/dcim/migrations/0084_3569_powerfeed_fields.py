from django.db import migrations, models


POWERFEED_TYPE_CHOICES = (
    (1, 'primary'),
    (2, 'redundant'),
)

POWERFEED_SUPPLY_CHOICES = (
    (1, 'ac'),
    (2, 'dc'),
)


def powerfeed_type_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_TYPE_CHOICES:
        PowerFeed.objects.filter(type=id).update(type=slug)


def powerfeed_supply_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_SUPPLY_CHOICES:
        PowerFeed.objects.filter(supply=id).update(supply=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0083_3569_cable_fields'),
    ]

    operations = [

        # PowerFeed.type
        migrations.AlterField(
            model_name='powerfeed',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_type_to_slug
        ),

        # PowerFeed.supply
        migrations.AlterField(
            model_name='powerfeed',
            name='supply',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_supply_to_slug
        ),

    ]
