from nautobot.core.api import OrderedDefaultRouter
from . import views


router = OrderedDefaultRouter()
router.APIRootView = views.ExtrasRootView

# Computed Fields
router.register("computed-fields", views.ComputedFieldViewSet)

# Config contexts
router.register("config-contexts", views.ConfigContextViewSet)

# Config context schemas
router.register("config-context-schemas", views.ConfigContextSchemaViewSet)

# ContentTypes
router.register("content-types", views.ContentTypeViewSet)

# Custom fields
router.register("custom-fields", views.CustomFieldViewSet)
router.register("custom-field-choices", views.CustomFieldChoiceViewSet)

# Custom Links
router.register("custom-links", views.CustomLinkViewSet)

# Export templates
router.register("export-templates", views.ExportTemplateViewSet)

# Git repositories
router.register("git-repositories", views.GitRepositoryViewSet)

# GraphQL Queries
router.register("graphql-queries", views.GraphQLQueryViewSet)

# Image attachments
router.register("image-attachments", views.ImageAttachmentViewSet)

# Jobs
router.register("jobs", views.JobViewSet, basename="job")

# Job Results
router.register("job-results", views.JobResultViewSet)

# Scheduled Jobs
router.register("scheduled-jobs", views.ScheduledJobViewSet)

# Change logging
router.register("object-changes", views.ObjectChangeViewSet)

# Relationships
router.register("relationships", views.RelationshipViewSet)
router.register("relationship-associations", views.RelationshipAssociationViewSet)

# Statuses
router.register("statuses", views.StatusViewSet)

# Tags
router.register("tags", views.TagViewSet)

# Webhooks
router.register("webhooks", views.WebhooksViewSet)

app_name = "extras-api"
urlpatterns = router.urls
