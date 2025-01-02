from django.db import migrations, models
import uuid

def copy_id_to_uuid(apps, schema_editor):
    # Access the SiteOnboarding model
    SiteOnboarding = apps.get_model('naas', 'SiteOnboarding')
    # Loop over all SiteOnboarding objects to set the new UUID field
    for site in SiteOnboarding.objects.all():
        site.new_id = uuid.uuid4()  # Generate and assign a new UUID
        site.save()

class Migration(migrations.Migration):

    dependencies = [
        ('naas', '0002_rename_num_devices_siteonboarding_device_number_and_more'),
    ]

    operations = [
        # Add the new UUID field
        migrations.AddField(
            model_name='siteonboarding',
            name='new_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        # Run the data migration to populate new_id field with UUID values
        migrations.RunPython(copy_id_to_uuid),
        
        # Remove the old 'id' field (which is a bigint field)
        migrations.RemoveField(
            model_name='siteonboarding',
            name='id',
        ),
        
        # Rename the new 'new_id' field to 'id'
        migrations.RenameField(
            model_name='siteonboarding',
            old_name='new_id',
            new_name='id',
        ),
    ]