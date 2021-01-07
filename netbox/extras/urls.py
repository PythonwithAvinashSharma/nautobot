from django.urls import path

from extras import views
from extras.models import ConfigContext, Tag


app_name = 'extras'
urlpatterns = [

    # Tags
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/add/', views.TagEditView.as_view(), name='tag_add'),
    path('tags/import/', views.TagBulkImportView.as_view(), name='tag_import'),
    path('tags/edit/', views.TagBulkEditView.as_view(), name='tag_bulk_edit'),
    path('tags/delete/', views.TagBulkDeleteView.as_view(), name='tag_bulk_delete'),
    path('tags/<str:slug>/edit/', views.TagEditView.as_view(), name='tag_edit'),
    path('tags/<str:slug>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
    path('tags/<str:slug>/changelog/', views.ObjectChangeLogView.as_view(), name='tag_changelog', kwargs={'model': Tag}),

    # Config contexts
    path('config-contexts/', views.ConfigContextListView.as_view(), name='configcontext_list'),
    path('config-contexts/add/', views.ConfigContextEditView.as_view(), name='configcontext_add'),
    path('config-contexts/edit/', views.ConfigContextBulkEditView.as_view(), name='configcontext_bulk_edit'),
    path('config-contexts/delete/', views.ConfigContextBulkDeleteView.as_view(), name='configcontext_bulk_delete'),
    path('config-contexts/<int:pk>/', views.ConfigContextView.as_view(), name='configcontext'),
    path('config-contexts/<int:pk>/edit/', views.ConfigContextEditView.as_view(), name='configcontext_edit'),
    path('config-contexts/<int:pk>/delete/', views.ConfigContextDeleteView.as_view(), name='configcontext_delete'),
    path('config-contexts/<int:pk>/changelog/', views.ObjectChangeLogView.as_view(), name='configcontext_changelog', kwargs={'model': ConfigContext}),

    # Image attachments
    path('image-attachments/<int:pk>/edit/', views.ImageAttachmentEditView.as_view(), name='imageattachment_edit'),
    path('image-attachments/<int:pk>/delete/', views.ImageAttachmentDeleteView.as_view(), name='imageattachment_delete'),

    # Change logging
    path('changelog/', views.ObjectChangeListView.as_view(), name='objectchange_list'),
    path('changelog/<int:pk>/', views.ObjectChangeView.as_view(), name='objectchange'),

    # Custom jobs
    path('custom-jobs/', views.CustomJobListView.as_view(), name='customjob_list'),
    path('custom-jobs/<str:module>.<str:name>/', views.CustomJobView.as_view(), name='customjob'),
    path('custom-jobs/results/', views.CustomJobResultListView.as_view(), name='customjob_result_list'),
    path('custom-jobs/results/<int:job_result_pk>/', views.CustomJobResultView.as_view(), name='customjob_result'),

    # Generic job results
    path('job-results/delete/', views.JobResultBulkDeleteView.as_view(), name='jobresult_bulk_delete'),
    path('job-results/<int:pk>/delete/', views.JobResultDeleteView.as_view(), name='jobresult_delete'),
]
