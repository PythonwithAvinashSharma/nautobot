from cacheops.signals import cache_invalidated, cache_read
from django_prometheus.models import model_deletes, model_inserts, model_updates
from prometheus_client import Counter

from .choices import ObjectChangeActionChoices
from .webhooks import enqueue_webhooks


#
# Change logging/webhooks
#

def _handle_changed_object(request, sender, instance, **kwargs):
    """
    Fires when an object is created or updated.
    """
    # Queue the object for processing once the request completes
    if kwargs.get('created'):
        action = ObjectChangeActionChoices.ACTION_CREATE
    elif 'created' in kwargs:
        action = ObjectChangeActionChoices.ACTION_UPDATE
    elif kwargs.get('action') in ['post_add', 'post_remove'] and kwargs['pk_set']:
        # m2m_changed with objects added or removed
        action = ObjectChangeActionChoices.ACTION_UPDATE
    else:
        return

    # Cache any custom field values to ensure they are captured during serialization
    if hasattr(instance, 'cache_custom_fields'):
        instance.cache_custom_fields()

    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        objectchange = instance.to_objectchange(action)
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Enqueue webhooks
    enqueue_webhooks(instance, request.user, request.id, action)

    # Increment metric counters
    if action == ObjectChangeActionChoices.ACTION_CREATE:
        model_inserts.labels(instance._meta.model_name).inc()
    elif action == ObjectChangeActionChoices.ACTION_UPDATE:
        model_updates.labels(instance._meta.model_name).inc()


def _handle_deleted_object(request, sender, instance, **kwargs):
    """
    Fires when an object is deleted.
    """
    # Record an ObjectChange if applicable
    if hasattr(instance, 'to_objectchange'):
        objectchange = instance.to_objectchange(ObjectChangeActionChoices.ACTION_DELETE)
        objectchange.user = request.user
        objectchange.request_id = request.id
        objectchange.save()

    # Enqueue webhooks
    enqueue_webhooks(instance, request.user, request.id, ObjectChangeActionChoices.ACTION_DELETE)

    # Increment metric counters
    model_deletes.labels(instance._meta.model_name).inc()


#
# Caching
#

cacheops_cache_hit = Counter('cacheops_cache_hit', 'Number of cache hits')
cacheops_cache_miss = Counter('cacheops_cache_miss', 'Number of cache misses')
cacheops_cache_invalidated = Counter('cacheops_cache_invalidated', 'Number of cache invalidations')


def cache_read_collector(sender, func, hit, **kwargs):
    if hit:
        cacheops_cache_hit.inc()
    else:
        cacheops_cache_miss.inc()


def cache_invalidated_collector(sender, obj_dict, **kwargs):
    cacheops_cache_invalidated.inc()


cache_read.connect(cache_read_collector)
cache_invalidated.connect(cache_invalidated_collector)
