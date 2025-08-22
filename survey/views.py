import os

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import FileResponse, Http404
from django.core.files import File

from utils import pdf_generator
from utils.media import get_media_url
from utils.survey_calcs import SurveyCalcs

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


class ReportView(APIView):
    """
    API endpoint to generate and render PDF reports from query params.
    """

    def get(self, request):
        serializer = serializers.ReportSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(
                {
                    "status": "error",
                    "message": "Parámetros inválidos",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # survey = serializer.validated_data["survey_id"]        # objeto Survey
        participant = serializer.validated_data["participant_id"]  # objeto Participant
        
        name = participant.name

        company = participant.company
        logo_path = get_media_url(company.logo)
        
        report = models.Report.objects.get(
            survey=serializer.validated_data["survey_id"],
            participant=serializer.validated_data["participant_id"],
        )

        # Generar el PDF (dummy data)
        survey_calcs = SurveyCalcs(
            participant=participant,
            survey=serializer.validated_data["survey_id"],
            company=company,
        )
        pdf_path = pdf_generator.generate_report(
            name=name,
            date=report.created_at.strftime("%d/%m/%Y"),
            grade_code="MDP",
            final_score=9.9,
            logo_path=logo_path,
            data=survey_calcs.get_company_totals(),
            resulting_paragraphs=survey_calcs.get_resulting_paragraphs(),
            resulting_titles=survey_calcs.get_resulting_titles(),
        )

        if not os.path.exists(pdf_path):
            raise Http404("El reporte no fue generado correctamente.")
        
        # Save file in database
        report, _ = models.Report.objects.get_or_create(
            survey=serializer.validated_data["survey_id"],
            participant=serializer.validated_data["participant_id"],
        )
        
        # Open the file and save it to FileField
        with open(pdf_path, "rb") as f:
            report.pdf_file.save(os.path.basename(pdf_path), File(f), save=True)

        # Devolver el PDF para renderizado en el navegador
        return FileResponse(
            open(pdf_path, "rb"),
            content_type="application/pdf",
            as_attachment=False,
            filename=f"{name}.pdf",
        )


class HasAnswerView(APIView):
    """ Validate if the user already answered the survey, to avoid duplicate answers """

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
            question_option__question__question_group__survey=survey
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