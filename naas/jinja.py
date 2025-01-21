# naas/jinja.py
from django.urls import reverse
from jinja2 import Environment, select_autoescape

def environment(**options):
    """
    Create and return a Jinja2 environment.
    """
    env = Environment(
        autoescape=select_autoescape(['html', 'xml']),
        **options
    )

    # Add custom filters and globals
    env.globals.update({
        'url': reverse,
    })
    
    return env