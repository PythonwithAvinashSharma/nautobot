# # naas/views.py

# from django.shortcuts import render



# # def AddNaaS(request):
# #     return render(request, "dashboard_plugin/add_naas.html")

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from naas.serializers import SiteOnboardingSerializer

# class SiteOnboardingAPIView(APIView):
#     def post(self, request):
#         serializer = SiteOnboardingSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Site onboarded successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# def NaaSView(request):
#     return render(request, "dashboard_plugin/naas.html")

from django.shortcuts import render, redirect

from nautobot.core.views import generic
from .models import SiteOnboarding
from .forms import SiteForm

class SiteOnboardingEditView(generic.ObjectEditView):

    def has_permission(self):
        # Custom permission logic
        return True

    queryset = SiteOnboarding.objects.all()
    model_form = SiteForm
    template_name = "naas/naas.html"
