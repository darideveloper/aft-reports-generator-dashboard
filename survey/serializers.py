from rest_framework import serializers

from survey.models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class InvitationCodeSerializer(serializers.Serializer):
    invitation_code = serializers.CharField(max_length=255)