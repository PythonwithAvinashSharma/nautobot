from django import template
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import View
from django_rq.queues import get_connection
from django_tables2 import RequestConfig
from rq import Worker

from netbox.views import generic
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.utils import copy_safe_request, count_related, shallow_compare_dict
from utilities.views import ContentTypePermissionRequiredMixin
from . import filters, forms, tables
from .choices import JobResultStatusChoices
from .models import ConfigContext, GitRepository, ImageAttachment, ObjectChange, JobResult, Status, Tag, TaggedItem
from .custom_jobs import get_custom_job, get_custom_jobs, run_custom_job
from .datasources import get_datasource_contents, enqueue_pull_git_repository_and_refresh_data


#
# Tags
#

class TagListView(generic.ObjectListView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    filterset = filters.TagFilterSet
    filterset_form = forms.TagFilterForm
    table = tables.TagTable


class TagEditView(generic.ObjectEditView):
    queryset = Tag.objects.all()
    model_form = forms.TagForm
    template_name = 'extras/tag_edit.html'


class TagDeleteView(generic.ObjectDeleteView):
    queryset = Tag.objects.all()


class TagBulkImportView(generic.BulkImportView):
    queryset = Tag.objects.all()
    model_form = forms.TagCSVForm
    table = tables.TagTable


class TagBulkEditView(generic.BulkEditView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    table = tables.TagTable
    form = forms.TagBulkEditForm


class TagBulkDeleteView(generic.BulkDeleteView):
    queryset = Tag.objects.annotate(
        items=count_related(TaggedItem, 'tag')
    )
    table = tables.TagTable


#
# Config contexts
#

# TODO: disallow (or at least warn) user from manually editing config contexts that
# have an associated owner, such as a Git repository

class ConfigContextListView(generic.ObjectListView):
    queryset = ConfigContext.objects.all()
    filterset = filters.ConfigContextFilterSet
    filterset_form = forms.ConfigContextFilterForm
    table = tables.ConfigContextTable
    action_buttons = ('add',)


class ConfigContextView(generic.ObjectView):
    queryset = ConfigContext.objects.all()

    def get_extra_context(self, request, instance):
        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('extras.configcontext.format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('extras.configcontext.format', 'json')
        else:
            format = 'json'

        return {
            'format': format,
        }


class ConfigContextEditView(generic.ObjectEditView):
    queryset = ConfigContext.objects.all()
    model_form = forms.ConfigContextForm
    template_name = 'extras/configcontext_edit.html'


class ConfigContextBulkEditView(generic.BulkEditView):
    queryset = ConfigContext.objects.all()
    filterset = filters.ConfigContextFilterSet
    table = tables.ConfigContextTable
    form = forms.ConfigContextBulkEditForm


class ConfigContextDeleteView(generic.ObjectDeleteView):
    queryset = ConfigContext.objects.all()


class ConfigContextBulkDeleteView(generic.BulkDeleteView):
    queryset = ConfigContext.objects.all()
    table = tables.ConfigContextTable


class ObjectConfigContextView(generic.ObjectView):
    base_template = None
    template_name = 'extras/object_configcontext.html'

    def get_extra_context(self, request, instance):
        source_contexts = ConfigContext.objects.restrict(request.user, 'view').get_for_object(instance)

        # Determine user's preferred output format
        if request.GET.get('format') in ['json', 'yaml']:
            format = request.GET.get('format')
            if request.user.is_authenticated:
                request.user.config.set('extras.configcontext.format', format, commit=True)
        elif request.user.is_authenticated:
            format = request.user.config.get('extras.configcontext.format', 'json')
        else:
            format = 'json'

        return {
            'rendered_context': instance.get_config_context(),
            'source_contexts': source_contexts,
            'format': format,
            'base_template': self.base_template,
            'active_tab': 'config-context',
        }


#
# Change logging
#

class ObjectChangeListView(generic.ObjectListView):
    queryset = ObjectChange.objects.all()
    filterset = filters.ObjectChangeFilterSet
    filterset_form = forms.ObjectChangeFilterForm
    table = tables.ObjectChangeTable
    template_name = 'extras/objectchange_list.html'
    action_buttons = ('export',)


class ObjectChangeView(generic.ObjectView):
    queryset = ObjectChange.objects.all()

    def get_extra_context(self, request, instance):
        related_changes = ObjectChange.objects.restrict(request.user, 'view').filter(
            request_id=instance.request_id
        ).exclude(
            pk=instance.pk
        )
        related_changes_table = tables.ObjectChangeTable(
            data=related_changes[:50],
            orderable=False
        )

        objectchanges = ObjectChange.objects.restrict(request.user, 'view').filter(
            changed_object_type=instance.changed_object_type,
            changed_object_id=instance.changed_object_id,
        )

        next_change = objectchanges.filter(time__gt=instance.time).order_by('time').first()
        prev_change = objectchanges.filter(time__lt=instance.time).order_by('-time').first()

        if prev_change:
            diff_added = shallow_compare_dict(
                prev_change.object_data,
                instance.object_data,
                exclude=['last_updated'],
            )
            diff_removed = {x: prev_change.object_data.get(x) for x in diff_added}
        else:
            # No previous change; this is the initial change that added the object
            diff_added = diff_removed = instance.object_data

        return {
            'diff_added': diff_added,
            'diff_removed': diff_removed,
            'next_change': next_change,
            'prev_change': prev_change,
            'related_changes_table': related_changes_table,
            'related_changes_count': related_changes.count()
        }


class ObjectChangeLogView(View):
    """
    Present a history of changes made to a particular object.

    base_template: The name of the template to extend. If not provided, "<app>/<model>.html" will be used.
    """
    base_template = None

    def get(self, request, model, **kwargs):

        # Handle QuerySet restriction of parent object if needed
        if hasattr(model.objects, 'restrict'):
            obj = get_object_or_404(model.objects.restrict(request.user, 'view'), **kwargs)
        else:
            obj = get_object_or_404(model, **kwargs)

        # Gather all changes for this object (and its related objects)
        content_type = ContentType.objects.get_for_model(model)
        objectchanges = ObjectChange.objects.restrict(request.user, 'view').prefetch_related(
            'user', 'changed_object_type'
        ).filter(
            Q(changed_object_type=content_type, changed_object_id=obj.pk) |
            Q(related_object_type=content_type, related_object_id=obj.pk)
        )
        objectchanges_table = tables.ObjectChangeTable(
            data=objectchanges,
            orderable=False
        )

        # Apply the request context
        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': get_paginate_count(request)
        }
        RequestConfig(request, paginate).configure(objectchanges_table)

        # Default to using "<app>/<model>.html" as the template, if it exists. Otherwise,
        # fall back to using base.html.
        if self.base_template is None:
            self.base_template = f"{model._meta.app_label}/{model._meta.model_name}.html"
            # TODO: This can be removed once an object view has been established for every model.
            try:
                template.loader.get_template(self.base_template)
            except template.TemplateDoesNotExist:
                self.base_template = 'base.html'

        return render(request, 'extras/object_changelog.html', {
            'object': obj,
            'table': objectchanges_table,
            'base_template': self.base_template,
            'active_tab': 'changelog',
        })


#
# Git repositories
#

class GitRepositoryListView(generic.ObjectListView):
    queryset = GitRepository.objects.all()
    # filterset = filters.GitRepositoryFilterSet
    # filterset_form = forms.GitRepositoryFilterForm
    table = tables.GitRepositoryTable
    template_name = 'extras/gitrepository_list.html'

    def extra_context(self):
        git_repository_content_type = ContentType.objects.get(app_label='extras', model='gitrepository')
        # Get the newest results for each repository name
        results = {
            r.name: r
            for r in JobResult.objects.filter(
                obj_type=git_repository_content_type,
                status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('completed').defer('data')
        }
        return {
            'job_results': results,
            'datasource_contents': get_datasource_contents('extras.GitRepository'),
        }


class GitRepositoryView(generic.ObjectView):
    queryset = GitRepository.objects.all()

    def get_extra_context(self, request, instance):
        return {
            'datasource_contents': get_datasource_contents('extras.GitRepository'),
        }


class GitRepositoryEditView(generic.ObjectEditView):
    queryset = GitRepository.objects.all()
    model_form = forms.GitRepositoryForm

    def alter_obj(self, obj, request, url_args, url_kwargs):
        # A GitRepository needs to know the originating request when it's saved so that it can enqueue using it
        obj.request = request
        return super().alter_obj(obj, request, url_args, url_kwargs)

    def get_return_url(self, request, obj):
        if request.method == "POST":
            return reverse('extras:gitrepository_result', kwargs={'slug': obj.slug})
        return super().get_return_url(request, obj)


class GitRepositoryDeleteView(generic.ObjectDeleteView):
    queryset = GitRepository.objects.all()


class GitRepositoryBulkImportView(generic.BulkImportView):
    queryset = GitRepository.objects.all()
    model_form = forms.GitRepositoryCSVForm
    table = tables.GitRepositoryBulkTable


class GitRepositoryBulkEditView(generic.BulkEditView):
    queryset = GitRepository.objects.all()
    filterset = filters.GitRepositoryFilterSet
    table = tables.GitRepositoryBulkTable
    form = forms.GitRepositoryBulkEditForm

    def alter_obj(self, obj, request, url_args, url_kwargs):
        # A GitRepository needs to know the originating request when it's saved so that it can enqueue using it
        obj.request = request
        return super().alter_obj(obj, request, url_args, url_kwargs)

    def extra_context(self):
        return {
            'datasource_contents': get_datasource_contents('extras.GitRepository'),
        }


class GitRepositoryBulkDeleteView(generic.BulkDeleteView):
    queryset = GitRepository.objects.all()
    table = tables.GitRepositoryBulkTable

    def extra_context(self):
        return {
            'datasource_contents': get_datasource_contents('extras.GitRepository'),
        }


class GitRepositorySyncView(View):
    def post(self, request, slug):
        if not request.user.has_perm('extras.change_gitrepository'):
            return HttpResponseForbidden()

        repository = get_object_or_404(GitRepository.objects.all(), slug=slug)

        # Allow execution only if RQ worker process is running
        if not Worker.count(get_connection('default')):
            messages.error(request, "Unable to sync Git repository: RQ worker process not running.")

        else:
            enqueue_pull_git_repository_and_refresh_data(repository, request)

        return redirect('extras:gitrepository_result', slug=slug)


class GitRepositoryResultView(ContentTypePermissionRequiredMixin, View):

    def get_required_permission(self):
        return 'extras.view_gitrepository'

    def get(self, request, slug):
        git_repository_content_type = ContentType.objects.get(app_label='extras', model='gitrepository')
        git_repository = get_object_or_404(GitRepository.objects.all(), slug=slug)
        job_result = JobResult.objects.filter(
            obj_type=git_repository_content_type, name=git_repository.name
        ).order_by('-created').first()
        return render(request, 'extras/gitrepository_result.html', {
            'base_template': 'extras/gitrepository.html',
            'object': git_repository,
            'result': job_result,
            'active_tab': 'result',
        })


#
# Image attachments
#

class ImageAttachmentEditView(generic.ObjectEditView):
    queryset = ImageAttachment.objects.all()
    model_form = forms.ImageAttachmentForm

    def alter_obj(self, imageattachment, request, args, kwargs):
        if not imageattachment.pk:
            # Assign the parent object based on URL kwargs
            model = kwargs.get('model')
            imageattachment.parent = get_object_or_404(model, pk=kwargs['object_id'])
        return imageattachment

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


class ImageAttachmentDeleteView(generic.ObjectDeleteView):
    queryset = ImageAttachment.objects.all()

    def get_return_url(self, request, imageattachment):
        return imageattachment.parent.get_absolute_url()


#
# Custom jobs
#

class CustomJobListView(ContentTypePermissionRequiredMixin, View):
    """
    Retrieve all of the available custom jobs from disk and the recorded JobResult (if any) for each.
    """
    def get_required_permission(self):
        return 'extras.view_customjob'

    def get(self, request):
        custom_jobs_dict = get_custom_jobs()
        custom_job_content_type = ContentType.objects.get(app_label='extras', model='customjob')
        # Get the newest results for each job name
        results = {
            r.name: r
            for r in JobResult.objects.filter(
                obj_type=custom_job_content_type,
                status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
            ).order_by('completed').defer('data')
        }

        # get_custom_jobs() gives us a nested dict {grouping: {module: {"name": name, "jobs": [job, job, job]}}}
        # But for presentation to the user we want to flatten this to {module_name: [job, job, job]}

        modules_dict = {}
        for grouping, modules in custom_jobs_dict.items():
            for module, entry in modules.items():
                module_custom_jobs = modules_dict.get(entry["name"], [])
                for custom_job_class in entry['jobs'].values():
                    custom_job = custom_job_class()
                    custom_job.result = results.get(custom_job.class_path, None)
                    module_custom_jobs.append(custom_job)
                if module_custom_jobs:
                    # TODO: should we sort module_custom_jobs by job name? Currently they're in source code order
                    modules_dict[entry["name"]] = module_custom_jobs

        return render(request, 'extras/customjob_list.html', {
            # Order the jobs listing by case-insensitive sorting of the module human-readable name
            'custom_jobs': sorted(modules_dict.items(), key=lambda kvpair: kvpair[0].lower()),
        })


class CustomJobView(ContentTypePermissionRequiredMixin, View):
    """
    View the parameters of a Custom Job and enqueue it if desired.
    """

    def get_required_permission(self):
        return 'extras.view_customjob'

    def get(self, request, class_path):
        custom_job_class = get_custom_job(class_path)
        if custom_job_class is None:
            raise Http404
        custom_job = custom_job_class()
        grouping, module, class_name = class_path.split("/", 2)

        form = custom_job.as_form(initial=request.GET)

        return render(request, 'extras/customjob.html', {
            'grouping': grouping,
            'module': module,
            'custom_job': custom_job,
            'form': form,
        })

    def post(self, request, class_path):
        if not request.user.has_perm('extras.run_customjob'):
            return HttpResponseForbidden()

        custom_job_class = get_custom_job(class_path)
        if custom_job_class is None:
            raise Http404
        custom_job = custom_job_class()
        grouping, module, class_name = class_path.split("/", 2)
        form = custom_job.as_form(request.POST, request.FILES)

        # Allow execution only if RQ worker process is running
        if not Worker.count(get_connection('default')):
            messages.error(request, "Unable to run custom job: RQ worker process not running.")

        elif form.is_valid():
            # Run the job. A new JobResult is created.
            commit = form.cleaned_data.pop('_commit')

            custom_job_content_type = ContentType.objects.get(app_label='extras', model='customjob')
            job_result = JobResult.enqueue_job(
                run_custom_job,
                custom_job.class_path,
                custom_job_content_type,
                request.user,
                data=form.cleaned_data,
                request=copy_safe_request(request),
                commit=commit,
            )

            return redirect('extras:customjob_jobresult', pk=job_result.pk)

        return render(request, 'extras/customjob.html', {
            'grouping': grouping,
            'module': module,
            'custom_job': custom_job,
            'form': form,
        })


class CustomJobResultView(ContentTypePermissionRequiredMixin, View):
    """
    Display a JobResult and its CustomJob data.
    """

    def get_required_permission(self):
        return 'extras.view_jobresult'

    def get(self, request, pk):
        custom_job_content_type = ContentType.objects.get(app_label='extras', model='customjob')
        job_result = get_object_or_404(JobResult.objects.all(), pk=pk, obj_type=custom_job_content_type)

        custom_job_class = get_custom_job(job_result.name)
        custom_job = custom_job_class() if custom_job_class else None

        return render(request, 'extras/customjob_result.html', {
            'custom_job': custom_job,
            'result': job_result,
        })


#
# JobResult
#

class JobResultListView(generic.ObjectListView):
    """
    List JobResults
    """
    queryset = JobResult.objects.all()
    filterset = filters.JobResultFilterSet
    filterset_form = forms.JobResultFilterForm
    table = tables.JobResultTable
    action_buttons = ()


class JobResultDeleteView(generic.ObjectDeleteView):
    queryset = JobResult.objects.all()


class JobResultBulkDeleteView(generic.BulkDeleteView):
    queryset = JobResult.objects.all()
    table = tables.JobResultTable


class JobResultView(ContentTypePermissionRequiredMixin, View):
    """
    Display a JobResult and its data.
    """

    def get_required_permission(self):
        return 'extras.view_jobresult'

    def get(self, request, pk):
        job_result = get_object_or_404(JobResult.objects.all(), pk=pk)

        associated_record = None
        custom_job = None
        custom_job_content_type = ContentType.objects.get(app_label='extras', model='customjob')
        if job_result.obj_type == custom_job_content_type:
            custom_job_class = get_custom_job(job_result.name)
            if custom_job_class is not None:
                custom_job = custom_job_class()
        else:
            model_class = job_result.obj_type.model_class()
            try:
                associated_record = model_class.objects.get(name=job_result.name)
            except model_class.DoesNotExist:
                pass

        return render(request, 'extras/jobresult.html', {
            'associated_record': associated_record,
            'custom_job': custom_job,
            'result': job_result,
        })


#
# Custom statuses
#

class StatusListView(generic.ObjectListView):
    """List `Status` objects."""
    queryset = Status.objects.all()
    filterset = filters.StatusFilterSet
    filterset_form = forms.StatusFilterForm
    table = tables.StatusTable


class StatusEditView(generic.ObjectEditView):
    """Edit a single `Status` object."""
    queryset = Status.objects.all()
    model_form = forms.StatusForm


class StatusBulkEditView(generic.BulkEditView):
    """Edit multiple `Status` objects."""
    queryset = Status.objects.all()
    table = tables.StatusTable
    form = forms.StatusBulkEditForm


class StatusBulkDeleteView(generic.BulkDeleteView):
    """Delete multiple `Status` objects."""
    queryset = Status.objects.all()
    table = tables.StatusTable


class StatusDeleteView(generic.ObjectDeleteView):
    """Delete a single `Status` object."""
    queryset = Status.objects.all()


class StatusBulkImportView(generic.BulkImportView):
    """Bulk CSV import of multiple `Status` objects."""
    queryset = Status.objects.all()
    model_form = forms.StatusCSVForm
    table = tables.StatusTable


class StatusView(generic.ObjectView):
    """Detail view for a single `Status` object."""
    queryset = Status.objects.all()
