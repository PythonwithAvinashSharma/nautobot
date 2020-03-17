from django import template as template_
from django.template.loader import get_template
from django.utils.safestring import mark_safe

from extras.plugins import get_content_classes


register = template_.Library()


def _get_registered_content(obj, method, context):
    """
    Given an object and a PluginTemplateContent method name and the template context, return all the
    registered content for the object's model.
    """
    html = ''

    plugin_template_classes = get_content_classes(obj._meta.label_lower)
    for plugin_template_class in plugin_template_classes:
        plugin_template_renderer = plugin_template_class(obj, context)
        try:
            content = getattr(plugin_template_renderer, method)()
        except NotImplementedError:
            # This content renderer class does not define content for this method
            continue
        html += content

    return mark_safe(html)


@register.simple_tag(takes_context=True)
def plugin_buttons(context, obj):
    """
    Fire signal to collect all buttons registered by plugins
    """
    return _get_registered_content(obj, 'buttons', context)


@register.simple_tag(takes_context=True)
def plugin_left_page(context, obj):
    """
    Fire signal to collect all left page content registered by plugins
    """
    return _get_registered_content(obj, 'left_page', context)


@register.simple_tag(takes_context=True)
def plugin_right_page(context, obj):
    """
    Fire signal to collect all right page content registered by plugins
    """
    return _get_registered_content(obj, 'right_page', context)


@register.simple_tag(takes_context=True)
def plugin_full_width_page(context, obj):
    """
    Fire signal to collect all full width page content registered by plugins
    """
    return _get_registered_content(obj, 'full_width_page', context)
