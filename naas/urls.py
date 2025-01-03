from django.urls import path
from .views import site_onboarding_view

urlpatterns = [
    path('site-onboarding', site_onboarding_view, name='naas'),
]