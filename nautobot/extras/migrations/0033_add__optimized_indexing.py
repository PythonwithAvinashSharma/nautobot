# Generated by Django 3.1.14 on 2022-04-13 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0032_tag_content_types_data_migration"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="objectchange",
            options={"get_latest_by": "time", "ordering": ["-time"]},
        ),
        migrations.AlterField(
            model_name="objectchange",
            name="changed_object_id",
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name="objectchange",
            name="request_id",
            field=models.UUIDField(db_index=True, editable=False),
        ),
        migrations.AlterIndexTogether(
            name="objectchange",
            index_together=set(),
        ),
        migrations.AddIndex(
            model_name="objectchange",
            index=models.Index(
                fields=["request_id", "changed_object_type_id", "changed_object_id"],
                name="extras_objectchange_triple_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="objectchange",
            index=models.Index(fields=["request_id", "changed_object_type_id"], name="extras_objectchange_double_idx"),
        ),
        migrations.AlterField(
            model_name="joblogentry",
            name="log_level",
            field=models.CharField(db_index=True, default="default", max_length=32),
        ),
        migrations.AlterField(
            model_name="jobresult",
            name="name",
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="relationshipassociation",
            name="destination_id",
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name="relationshipassociation",
            name="source_id",
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="name",
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="imageattachment",
            name="name",
            field=models.CharField(blank=True, db_index=True, max_length=50),
        ),
        migrations.AlterField(
            model_name="imageattachment",
            name="object_id",
            field=models.UUIDField(db_index=True),
        ),
        migrations.AlterField(
            model_name="job",
            name="grouping",
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="job",
            name="name",
            field=models.CharField(db_index=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="scheduledjob",
            name="job_class",
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="scheduledjob",
            name="name",
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="scheduledjob",
            name="queue",
            field=models.CharField(blank=True, db_index=True, default=None, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name="scheduledjob",
            name="task",
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]
