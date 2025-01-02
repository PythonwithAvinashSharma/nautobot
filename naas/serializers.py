from rest_framework import serializers
from .models import SiteOnboarding

class SiteOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteOnboarding
        fields = '__all__'
