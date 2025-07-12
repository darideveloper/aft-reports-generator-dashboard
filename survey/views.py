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
            invitation_code = serializer.validated_data['invitation_code']

            # Do something with invitation_code (e.g., lookup, validate, etc.)
            result = {
                "message": "Invitation code received",
                "invitation_code": invitation_code
            }

            return Response(result, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)