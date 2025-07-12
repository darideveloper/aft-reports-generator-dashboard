from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from survey import serializers, models


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer

    def get_queryset(self):
        return self.queryset.filter(is_active=True)


class InvitationCodeView(APIView):
    def post(self, request):
        serializer = serializers.InvitationCodeSerializer(data=request.data)
        if serializer.is_valid():
            invitation_code = serializer.validated_data["invitation_code"]

            try:
                company = models.Company.objects.get(
                    invitation_code=invitation_code, is_active=True
                )
            except models.Company.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid or inactive invitation code.",
                        "data": [],
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            data = {
                "status": "ok",
                "message": "Valid invitation code.",
                "data": {
                    "id": company.id,
                    "name": company.name,
                    "details": company.details,
                },
            }

            return Response(data, status=status.HTTP_200_OK)

        return Response(
            {
                "status": "error",
                "message": "Invalid data",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
