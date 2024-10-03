# Generated by Django 4.2.15 on 2024-08-20 14:58

from django.db import migrations

from nautobot.extras.choices import JobQueueTypeChoices


def migrate_task_queues_to_job_queues(apps, schema):
    # Get the relevant models
    Job = apps.get_model("extras", "Job")
    ScheduledJob = apps.get_model("extras", "ScheduledJob")
    JobQueue = apps.get_model("extras", "JobQueue")

    # should always create default job queue
    JobQueue.objects.get_or_create(name="default", defaults={"queue_type": JobQueueTypeChoices.TYPE_CELERY})
    for job in Job.objects.all():
        task_queues = job.task_queues
        # Go through each task_queue
        # make or get the corresponding job_queue object and assign it to the job
        for task_queue in task_queues:
            job_queue, _ = JobQueue.objects.get_or_create(
                name=task_queue, defaults={"queue_type": JobQueueTypeChoices.TYPE_CELERY}
            )
            job.job_queues.add(job_queue)

    for sj in ScheduledJob.objects.all():
        queue = sj.queue
        job_queue = None
        if queue:
            job_queue, _ = JobQueue.objects.get_or_create(
                name=queue, defaults={"queue_type": JobQueueTypeChoices.TYPE_CELERY}
            )
        sj.job_queue = job_queue
        sj.save()


def reverse_migrate_task_queues_to_job_queues(apps, schema):
    Job = apps.get_model("extras", "Job")
    ScheduledJob = apps.get_model("extras", "ScheduledJob")
    JobQueueAssignment = apps.get_model("extras", "JobQueueAssignment")

    for job in Job.objects.all():
        queue_names = job.job_queues.all().values_list("name", flat=True)
        job.task_queues = queue_names
        job.save()
    JobQueueAssignment.objects.all().delete()

    for sj in ScheduledJob.objects.all():
        job_queue = sj.job_queue
        if job_queue:
            sj.queue = job_queue.name
        else:
            sj.queue = ""
        sj.job_queue = None
        sj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0116_create_job_queue_model"),
    ]

    operations = [
        migrations.RunPython(
            code=migrate_task_queues_to_job_queues,
            reverse_code=reverse_migrate_task_queues_to_job_queues,
        )
    ]
