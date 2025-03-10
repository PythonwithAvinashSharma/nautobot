# DCIM

## Replace Site and Region with Location Model

In Nautobot 2.0.0, all the `Region` and `Site` related data models are being migrated to use `Location`. Below is a comprehensive guide for Nautobot App developers to migrate their `Region` and `Site` related data models to `Location`.

We will be using `ExampleModel` as a relatively simple and hands-on example throughout this guide to better your understanding of the migration process.

### Before you Begin

!!! warning
    You **must** perform these steps before proceeding. Failing to follow them properly could result in data loss. **Always** backup your database before performing any migration steps.  
Before you follow the guide, please make sure that these operations are completed:  

1. Make sure your working Nautobot is on Version 1.5.x with baseline migrations all run.  
2. Stop Nautobot Server.  
3. Create a [backup](../../../../user-guide/administration/upgrading/database-backup.md) of your Nautobot database.
4. Update installed version of Nautobot to 2.0.0.  
5. Run `nautobot-server migrate dcim 0034_migrate_region_and_site_data_to_locations`. (This operation will ensure that `("dcim", "0034_migrate_region_and_site_data_to_locations")` is the latest migration applied to your Nautobot instance and that `("dcim", "0034_remove_region_and_site")` is **not** applied. **Failure to complete this step will result in data loss**)  

After you complete those operations, follow the guide below for each of your installed apps to:  

1. Make all necessary migration files for each app.  
2. Run `nautobot-server migrate [app_name]` to apply those migration files to each app.  
3. Finally, Start Nautobot Server after **all** the migration files are applied and **all** your affected apps are updated.  

### Add Location Fields to Site and Region Related Data Models

If the `ExampleModel` currently has a `site` ForeignKey field but it does not have a `location` ForeignKey field, you will need to add the `location` field before any other migrations in this guide.

!!! note
    You can skip this step only if your data models already have both a `site` (or `region`) field and a `location` field.

```python
# models.py

class ExampleModel(OrganizationalModel):
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=20, help_text="The name of this Example.")
...
```

**DO NOT** delete the `site` ForeignKey field yet. As a first step, just add a `ForeignKey` to `dcim.Location` with all other arguments identical to the existing `dcim.Site` `ForeignKey`:

```python
# models.py

class ExampleModel(OrganizationalModel):
    site = models.ForeignKey(
        to="dcim.Site",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    location = models.ForeignKey(
        to="dcim.Location",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=20, help_text="The name of this Example.")
...
```

Make the migration file by running `nautobot-server makemigrations [app_name] -n [migration_name]`, for example:

```shell
nautobot-server makemigrations example_app -n add_location_field_to_example_model
```

### Create an Empty Migration File and Write the Data Migration

After you make sure that all `Site`/`Region` related models have `location` fields on them, it is time to migrate `Site`/`Region` references in your data to `Location`.

Django doesn't automatically know how to do this; we have to create an empty migration file and write the migration script ourselves. This is also known as a [data migration](https://docs.djangoproject.com/en/3.2/topics/migrations/#data-migrations).

Create a migration file first by running `nautobot-server makemigrations [app_name] -n [migration_file_name] --empty`, for example:

```shell
nautobot-server makemigrations example_app -n migrate_app_data_from_site_to_location --empty
```

The empty migration file will look like this with the only dependency being our previous migration that added a `location` ForeignKey field to our `ExampleModel`:

```python
# Generated by Django 3.2.17 on 2023-02-22 15:38
# 0008_migrate_example_model_data_from_site_to_location

from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("example_app", "0007_add_location_field_to_example_model"),
    ]
    operations = []
```

!!! warning
    First we need to add a mandatory dependency to a Nautobot 2.0 migration file, namely `("dcim", "0034_migrate_region_and_site_data_to_locations")`. This dependent migration is very important as it creates the `Location` and `LocationType` records corresponding to the existing `Site`/`Region` records, which you will need to reference to migrate your data.
    **Without it, your data migration might not work!**

```python
    dependencies = [
        # The dcim migration creates the Site Type and Region Type Locations that
        # your data models are migrating to. It has to be run **before** this migration.
        ("dcim", "0034_migrate_region_and_site_data_to_locations"),
        ("example_app", "0007_add_location_field_to_example_model"),
    ]
```

Before we write the function that will perform the data migration, please note that Nautobot's `dcim` `0029` migration helpfully added and populated a Foreign Key called `migrated_location` on all `Region` and `Site` records. `migrated_location` stores the new location records that have the same names and other attributes as their respective `Sites`. That means all you need to do is query `ExampleModel` instances that have non-null `site` fields and null `location` fields and point the `location` field on your object to the site's `migrated_location` attribute, for example:

```python
example_model.location = example_model.site.migrated_location
```

Below is what the function might look like:

```python
def migrate_example_model_data_to_locations(apps, schema_editor):
    # Always use the provided `apps` to look up models
    # rather than importing them directly!
    ExampleModel = apps.get_model("example_app", "examplemodel")
    LocationType = apps.get_model("dcim", "locationtype")
    Location = apps.get_model("dcim", "location")

    # Query ExampleModel instances with non-null site field
    example_models = ExampleModel.objects.filter(
        site__isnull=False, location__isnull=True
    ).select_related("site", "location")
    for example_model in example_models:
        # Point the location field to the corresponding
        # "Site" LocationType Location stored in migrate_location
        example_model.location = example_model.site.migrated_location
    ExampleModel.objects.bulk_update(example_models, ["location"], 1000)
```

Finally, we need to add `migrations.RunPython` to the `operations` attribute in the migration class to execute this function when the migration is applied:

```python
    operations = [
        migrations.RunPython(
            # Execute the function
            code=migrate_example_model_data_to_locations,
            reverse_code=migrations.operations.special.RunPython.noop,
        )
    ]

```

The final migration file might look like this:

```python
# Generated by Django 3.2.17 on 2023-02-22 15:38
# 0008_migrate_example_model_data_from_site_to_location

from django.db import migrations

def migrate_example_model_data_to_locations(apps, schema_editor):

    ExampleModel = apps.get_model("example_app", "examplemodel")
    LocationType = apps.get_model("dcim", "locationtype")
    Location = apps.get_model("dcim", "location")
    # Get "Site" LocationType
    site_location_type = LocationType.objects.get(name="Site")

    # Query ExampleModel instances with non-null site field
    example_models = ExampleModel.objects.filter(
        site__isnull=False, location__isnull=True
    ).select_related("site", "location")
    for example_model in example_models:
        # Point the location field to the corresponding "Site" LocationType Location
        # with the same name.
        example_model.location = example_model.site.migrated_location
    ExampleModel.objects.bulk_update(example_models, ["location"], 1000)

class Migration(migrations.Migration):
    dependencies = [
        # The dcim migration creates the Site Type and Region Type Locations that
        # your data models are migrating to.
        # Therefore, It has to be run **before** this migration.
        ("dcim", "0034_migrate_region_and_site_data_to_locations"),
        ("example_app", "0007_add_location_field_to_example_model"),
    ]
    operations = [
        migrations.RunPython(
            # Execute the function
            code=migrate_example_model_data_to_locations,
            reverse_code=migrations.operations.special.RunPython.noop,
        )
    ]
```

### Remove Site/Region Related Fields from Migrated Data Models

After the data migration is successful, we need to remove the `site`/`region` fields from your data model so that Nautobot will be able to remove the `Site` and `Region` models. Note that we need to remove those attributes in a separate migration file from the previous one, as it's never a good practice to combine data migrations and schema migrations in the same file. You can do this by simply removing the `site`/`region` attributes from your model class:

```python
# models.py
class ExampleModel(OrganizationalModel):
    # note that site field is gone
    location = models.ForeignKey(
        to="dcim.Location",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=20, help_text="The name of this Example.")
...
```

After removing the `site` attribute, make the migration file by running `nautobot-server makemigrations [app_name] -n [migration_name]`, for example:

```shell
nautobot-server makemigrations example_app -n remove_site_field_from_example_model
```

The migration file might look like this:

```python
# Generated by Django 3.2.17 on 2023-02-22 17:09
# 0009_remove_site_field_from_example_model.py

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('example_app', '0008_migrate_example_model_data_from_site_to_location'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examplemodel',
            name='site',
        ),
    ]
```

!!! important
    Before you apply this migration, you have to add a `run_before` attribute in this migration file to make sure that you remove `site`/`region` fields before `Site` and `Region` models themselves are removed. **Without it, your migration files might be out of order and your app will not start**.

```python
    # Ensure this migration is run before the migration that removes Region and Site Models
    run_before = [
        ("dcim", "0040_remove_region_and_site"),
    ]
```

The final migration file might look like this:

```python
# Generated by Django 3.2.17 on 2023-02-22 17:09
# 0009_remove_site_field_from_example_model.py

from django.db import migrations

class Migration(migrations.Migration):

    # Ensure this migration is run before the migration that removes Region and Site Models
    run_before = [
        ("dcim", "0040_remove_region_and_site"),
    ]
    dependencies = [
        ("example_app", "0008_migrate_example_model_data_from_site_to_location"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="examplemodel",
            name="site",
        ),
    ]
```

Apply the migration files by running `nautobot-server migrate [app_name]`, for example:

```shell
nautobot-server migrate example_app
```
