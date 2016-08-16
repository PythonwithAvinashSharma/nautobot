from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import ValidationError
from django.db import models
from django.http import HttpResponse
from django.template import Template, Context
from django.utils.safestring import mark_safe


CUSTOMFIELD_MODELS = (
    'site', 'rack', 'device',                               # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf',      # IPAM
    'provider', 'circuit',                                  # Circuits
    'tenant',                                               # Tenants
)

CF_TYPE_TEXT = 100
CF_TYPE_INTEGER = 200
CF_TYPE_BOOLEAN = 300
CF_TYPE_DATE = 400
CF_TYPE_SELECT = 500
CUSTOMFIELD_TYPE_CHOICES = (
    (CF_TYPE_TEXT, 'Text'),
    (CF_TYPE_INTEGER, 'Integer'),
    (CF_TYPE_BOOLEAN, 'Boolean (true/false)'),
    (CF_TYPE_DATE, 'Date'),
    (CF_TYPE_SELECT, 'Selection'),
)

GRAPH_TYPE_INTERFACE = 100
GRAPH_TYPE_PROVIDER = 200
GRAPH_TYPE_SITE = 300
GRAPH_TYPE_CHOICES = (
    (GRAPH_TYPE_INTERFACE, 'Interface'),
    (GRAPH_TYPE_PROVIDER, 'Provider'),
    (GRAPH_TYPE_SITE, 'Site'),
)

EXPORTTEMPLATE_MODELS = [
    'site', 'rack', 'device', 'consoleport', 'powerport', 'interfaceconnection',    # DCIM
    'aggregate', 'prefix', 'ipaddress', 'vlan',                                     # IPAM
    'provider', 'circuit',                                                          # Circuits
    'tenant',                                                                       # Tenants
]

ACTION_CREATE = 1
ACTION_IMPORT = 2
ACTION_EDIT = 3
ACTION_BULK_EDIT = 4
ACTION_DELETE = 5
ACTION_BULK_DELETE = 6
ACTION_CHOICES = (
    (ACTION_CREATE, 'created'),
    (ACTION_IMPORT, 'imported'),
    (ACTION_EDIT, 'modified'),
    (ACTION_BULK_EDIT, 'bulk edited'),
    (ACTION_DELETE, 'deleted'),
    (ACTION_BULK_DELETE, 'bulk deleted')
)


class CustomFieldModel(object):

    def custom_fields(self):

        # Find all custom fields applicable to this type of object
        content_type = ContentType.objects.get_for_model(self)
        fields = CustomField.objects.filter(obj_type=content_type)

        # If the object exists, populate its custom fields with values
        if hasattr(self, 'pk'):
            values = CustomFieldValue.objects.filter(obj_type=content_type, obj_id=self.pk).select_related('field')
            values_dict = {cfv.field_id: cfv.value for cfv in values}
            return {field: values_dict.get(field.pk) for field in fields}
        else:
            return {field: None for field in fields}


class CustomField(models.Model):
    obj_type = models.ManyToManyField(ContentType, related_name='custom_fields', verbose_name='Object(s)',
                                      limit_choices_to={'model__in': CUSTOMFIELD_MODELS},
                                      help_text="The object(s) to which this field applies.")
    type = models.PositiveSmallIntegerField(choices=CUSTOMFIELD_TYPE_CHOICES, default=CF_TYPE_TEXT)
    name = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=50, blank=True, help_text="Name of the field as displayed to users (if not "
                                                                  "provided, the field's name will be used)")
    description = models.CharField(max_length=100, blank=True)
    required = models.BooleanField(default=False, help_text="Determines whether this field is required when creating "
                                                            "new objects or editing an existing object.")
    default = models.CharField(max_length=100, blank=True, help_text="Default value for the field. N/A for selection "
                                                                     "fields.")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.label or self.name.capitalize()


class CustomFieldValue(models.Model):
    field = models.ForeignKey('CustomField', related_name='values')
    obj_type = models.ForeignKey(ContentType, related_name='+', on_delete=models.PROTECT)
    obj_id = models.PositiveIntegerField()
    obj = GenericForeignKey('obj_type', 'obj_id')
    val_int = models.BigIntegerField(blank=True, null=True)
    val_char = models.CharField(max_length=100, blank=True)
    val_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['obj_type', 'obj_id']
        unique_together = ['field', 'obj_type', 'obj_id']

    def __unicode__(self):
        return '{} {}'.format(self.obj, self.field)

    @property
    def value(self):
        if self.field.type == CF_TYPE_INTEGER:
            return self.val_int
        if self.field.type == CF_TYPE_BOOLEAN:
            return bool(self.val_int) if self.val_int is not None else None
        if self.field.type == CF_TYPE_DATE:
            return self.val_date
        if self.field.type == CF_TYPE_SELECT:
            return CustomFieldChoice.objects.get(pk=self.val_int) if self.val_int else None
        return self.val_char

    @value.setter
    def value(self, value):
        if self.field.type == CF_TYPE_INTEGER:
            self.val_int = value
        elif self.field.type == CF_TYPE_BOOLEAN:
            self.val_int = int(bool(value)) if value is not None else None
        elif self.field.type == CF_TYPE_DATE:
            self.val_date = value
        elif self.field.type == CF_TYPE_SELECT:
            # Could be ModelChoiceField or TypedChoiceField
            self.val_int = value.id if hasattr(value, 'id') else value
        else:
            self.val_char = value

    def save(self, *args, **kwargs):
        if (self.field.type == CF_TYPE_TEXT and self.value == '') or self.value is None:
            if self.pk:
                self.delete()
        else:
            super(CustomFieldValue, self).save(*args, **kwargs)


class CustomFieldChoice(models.Model):
    field = models.ForeignKey('CustomField', related_name='choices', limit_choices_to={'type': CF_TYPE_SELECT},
                              on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    weight = models.PositiveSmallIntegerField(default=100)

    class Meta:
        ordering = ['field', 'weight', 'value']
        unique_together = ['field', 'value']

    def __unicode__(self):
        return self.value

    def clean(self):
        if self.field.type != CF_TYPE_SELECT:
            raise ValidationError("Custom field choices can only be assigned to selection fields.")


class Graph(models.Model):
    type = models.PositiveSmallIntegerField(choices=GRAPH_TYPE_CHOICES)
    weight = models.PositiveSmallIntegerField(default=1000)
    name = models.CharField(max_length=100, verbose_name='Name')
    source = models.CharField(max_length=500, verbose_name='Source URL')
    link = models.URLField(verbose_name='Link URL', blank=True)

    class Meta:
        ordering = ['type', 'weight', 'name']

    def __unicode__(self):
        return self.name

    def embed_url(self, obj):
        template = Template(self.source)
        return template.render(Context({'obj': obj}))

    def embed_link(self, obj):
        if self.link is None:
            return ''
        template = Template(self.link)
        return template.render(Context({'obj': obj}))


class ExportTemplate(models.Model):
    content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in': EXPORTTEMPLATE_MODELS})
    name = models.CharField(max_length=200)
    template_code = models.TextField()
    mime_type = models.CharField(max_length=15, blank=True)
    file_extension = models.CharField(max_length=15, blank=True)

    class Meta:
        ordering = ['content_type', 'name']
        unique_together = [
            ['content_type', 'name']
        ]

    def __unicode__(self):
        return u'{}: {}'.format(self.content_type, self.name)

    def to_response(self, context_dict, filename):
        """
        Render the template to an HTTP response, delivered as a named file attachment
        """
        template = Template(self.template_code)
        mime_type = 'text/plain' if not self.mime_type else self.mime_type
        response = HttpResponse(
            template.render(Context(context_dict)),
            content_type=mime_type
        )
        if self.file_extension:
            filename += '.{}'.format(self.file_extension)
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response


class TopologyMap(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    site = models.ForeignKey('dcim.Site', related_name='topology_maps', blank=True, null=True)
    device_patterns = models.TextField(help_text="Identify devices to include in the diagram using regular expressions,"
                                                 "one per line. Each line will result in a new tier of the drawing. "
                                                 "Separate multiple regexes on a line using commas. Devices will be "
                                                 "rendered in the order they are defined.")
    description = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

    @property
    def device_sets(self):
        if not self.device_patterns:
            return None
        return [line.strip() for line in self.device_patterns.split('\n')]


class UserActionManager(models.Manager):

    # Actions affecting a single object
    def log_action(self, user, obj, action, message):
        self.model.objects.create(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.pk,
            user=user,
            action=action,
            message=message,
        )

    def log_create(self, user, obj, message=''):
        self.log_action(user, obj, ACTION_CREATE, message)

    def log_edit(self, user, obj, message=''):
        self.log_action(user, obj, ACTION_EDIT, message)

    def log_delete(self, user, obj, message=''):
        self.log_action(user, obj, ACTION_DELETE, message)

    # Actions affecting multiple objects
    def log_bulk_action(self, user, content_type, action, message):
        self.model.objects.create(
            content_type=content_type,
            user=user,
            action=action,
            message=message,
        )

    def log_import(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_IMPORT, message)

    def log_bulk_edit(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_EDIT, message)

    def log_bulk_delete(self, user, content_type, message=''):
        self.log_bulk_action(user, content_type, ACTION_BULK_DELETE, message)


class UserAction(models.Model):
    """
    A record of an action (add, edit, or delete) performed on an object by a User.
    """
    time = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name='actions', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    action = models.PositiveSmallIntegerField(choices=ACTION_CHOICES)
    message = models.TextField(blank=True)

    objects = UserActionManager()

    class Meta:
        ordering = ['-time']

    def __unicode__(self):
        if self.message:
            return u'{} {}'.format(self.user, self.message)
        return u'{} {} {}'.format(self.user, self.get_action_display(), self.content_type)

    def icon(self):
        if self.action in [ACTION_CREATE, ACTION_IMPORT]:
            return mark_safe('<i class="glyphicon glyphicon-plus text-success"></i>')
        elif self.action in [ACTION_EDIT, ACTION_BULK_EDIT]:
            return mark_safe('<i class="glyphicon glyphicon-pencil text-warning"></i>')
        elif self.action in [ACTION_DELETE, ACTION_BULK_DELETE]:
            return mark_safe('<i class="glyphicon glyphicon-remove text-danger"></i>')
        else:
            return ''
