import sys
from django.db import models


def check_for_duplicates_with_natural_key_fields_in_migration(model_class, natural_key_fields):
    """
    Migration helper method to raise a RuntimeError if the existing model_class data contains incorrigible duplicate records.

    Args:
        model_class: Nautobot model class (Device, VirtualChassis and etc)
        natural_key_fields: Names of the fields serving as natural keys for the model_class.
    """
    duplicate_records = (
        model_class.objects.values(*natural_key_fields)
        .order_by()
        .annotate(count=models.Count("pk"))
        .filter(count__gt=1)
    )
    print("\n    Checking for duplicate records ...")
    if duplicate_records.exists():
        if len(natural_key_fields) > 1:
            print(
                f"    Duplicate {model_class.__name__} attributes '{*natural_key_fields,}' detected: {list(duplicate_records.values_list(*natural_key_fields))}",
                file=sys.stderr,
            )
        else:
            print(
                f"    Duplicate {model_class.__name__} attribute '{natural_key_fields[0]}' detected: {list(duplicate_records.values_list(natural_key_fields[0], flat=True))}",
                file=sys.stderr,
            )
        print(
            f"    Unable to proceed with migrations; in Nautobot 2.0+ attribute(s) {natural_key_fields} for these records must be unique.",
            file=sys.stderr,
        )
        raise RuntimeError("Duplicate records must be manually resolved before migrating.")


def update_object_change_ct_for_replaced_models(apps, new_app_model, replaced_apps_models, reverse_migration=False):
    """
    Update the ObjectChange content type references for replaced models to their new models' content type.

    Args:
        - apps: An instance of the Django 'apps' object.
        - new_app_model: A dict containing information about the new model, including the 'app_name' and 'model' names.
        - replaced_apps_models: A list of dict, each containing information about a replaced model, including the 'app_name' and 'model' names.
        - reverse_migration: If set to True, reverse the migration by updating references from new models to replaced models.
    """
    ObjectChange = apps.get_model("extras", "ObjectChange")
    NewModel = apps.get_model(new_app_model["app_name"], new_app_model["model"])
    ContentType = apps.get_model("contenttypes", "ContentType")
    new_model_ct = ContentType.objects.get_for_model(NewModel)

    for replaced_model in replaced_apps_models:
        ReplacedModel = apps.get_model(replaced_model["app_name"], replaced_model["model"])
        replaced_model_ct = ContentType.objects.get_for_model(ReplacedModel)

        if reverse_migration:
            ObjectChange.objects.filter(changed_object_type=new_model_ct).update(changed_object_type=replaced_model_ct)
            ObjectChange.objects.filter(related_object_type=new_model_ct).update(related_object_type=replaced_model_ct)
        else:
            ObjectChange.objects.filter(changed_object_type=replaced_model_ct).update(
                changed_object_type=new_model_ct
            )
            ObjectChange.objects.filter(related_object_type=replaced_model_ct).update(related_object_type=new_model_ct)
