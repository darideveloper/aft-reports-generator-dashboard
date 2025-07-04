from rest_framework import viewsets

from survey import serializers, models


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer

    def get_queryset(self):
        return self.queryset.filter(is_active=True)
