# naas/urls.py

# from django.urls import path
# from . import views

# app_name = "naas"

# urlpatterns = [
#     path("", views.NaaSView, name="naas"),
#     path("", views.AddNaaS, name="add_naas"),
# ]
from django.urls import path
from . import views

urlpatterns = [
    path("site-onboarding", views.SiteOnboardingEditView.as_view(), name="naas"),
    #path("site-onboarding/add/", views.SiteOnboardingAPIView.as_view(), name="add_naas"),
]