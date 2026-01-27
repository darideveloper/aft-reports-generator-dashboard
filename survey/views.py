from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from survey import serializers, models


class InvitationCodeView(APIView):
    def post(self, request):
        serializer = serializers.InvitationCodeSerializer(data=request.data)
        if serializer.is_valid():

            # Validate data structure
            invitation_code = serializer.validated_data["invitation_code"]

            # Check if the invitation code is valid
            try:
                company = models.Company.objects.get(
                    invitation_code=invitation_code, is_active=True
                )
            except models.Company.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid or inactive invitation code.",
                        "data": {},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the company is active
            if not company.is_active:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid or inactive invitation code.",
                        "data": {},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Valid
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


# Get api endpoint
class SurveyDetailView(viewsets.ReadOnlyModelViewSet):
    queryset = models.Survey.objects.all()
    serializer_class = serializers.SurveyDetailSerializer

    def get_queryset(self):
        return self.queryset


class HasAnswerView(APIView):
    """Validate if the user already answered the survey, to avoid duplicate answers"""

    def post(self, request):
        serializer = serializers.HasAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Invalid data",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        survey = serializer.validated_data["survey_id"]

        has_answer = models.Answer.objects.filter(
            participant__email=email,
            question_option__question__question_group__survey=survey,
        ).exists()

        # Return true if not has answer

        data = {
            "status": "error",
            "message": "Participant with answer.",
            "data": {
                "has_answer": True,
            },
        }
        if not has_answer:
            data = {
                "status": "ok",
                "message": "Participant without answer.",
                "data": {
                    "has_answer": False,
                },
            }

        return Response(data, status=status.HTTP_200_OK)


class ResponseView(APIView):
    def post(self, request):
        serializer = serializers.ResponseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Invalid data",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        participant, options, report = serializer.save()

        # Delete progress after successful submission
        models.FormProgress.objects.filter(
            email=participant.email, survey=report.survey
        ).delete()

        return Response(
            {
                "status": "ok",
                "message": "Participant and answers registered successfully",
                "data": {
                    "participant_id": participant.id,
                    "answers_count": len(options),
                    "report_id": report.id,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class FormProgressView(APIView):
    def get(self, request):
        email = request.query_params.get("email")
        survey_id = request.query_params.get("survey")

        if not email or not survey_id:
            return Response(
                {"detail": "email and survey parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            progress = models.FormProgress.objects.get(email=email, survey_id=survey_id)
            serializer = serializers.FormProgressSerializer(progress)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.FormProgress.DoesNotExist:
            return Response(
                {"detail": "Progress not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        email = request.data.get("email")
        survey_id = request.data.get("survey")

        if not email or not survey_id:
            return Response(
                {"detail": "email and survey are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Handle Upsert logic
        try:
            progress = models.FormProgress.objects.get(email=email, survey_id=survey_id)
            serializer = serializers.FormProgressSerializer(
                progress, data=request.data, partial=True
            )
        except models.FormProgress.DoesNotExist:
            serializer = serializers.FormProgressSerializer(data=request.data)

        if serializer.is_valid():
            # Extract guestCode for company linking
            data_blob = request.data.get("data", {})
            guest_code = data_blob.get("guestCodeResponse", {}).get("guestCode")
            company = None
            if guest_code:
                company = models.Company.objects.filter(
                    invitation_code=guest_code, is_active=True
                ).first()

            progress = serializer.save(company=company)
            # Update expires_at on every save to extend validity
            progress.expires_at = models.get_default_expires_at()
            progress.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        email = request.query_params.get("email")
        survey_id = request.query_params.get("survey")

        if not email or not survey_id:
            return Response(
                {"detail": "email and survey parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        models.FormProgress.objects.filter(email=email, survey_id=survey_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
