import os
import random
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from core import choices
from survey import models, serializers

from utils.survey_calcs_group import SurveyCalcsGroupTexts


class GroupReportPDFView(View):
    NOMINAL_RANKING_CHUNK_SIZE = 16
    HEATMAP_CHUNK_SIZE = 15
    STRATEGIC_CHUNK_SIZE = 40  # 2 columns × ~20 names per column

    def _chunk_list(self, lst: list, chunk_size: int) -> list[list]:
        """
        Split a list into chunks of a specified size.
        """
        if not lst:
            return []
        return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]

    def _get_range_es(self, range_val: str) -> str:
        """
        Convert average range to Spanish
        """
        ranges = {
            "low": "básico",
            "medium": "intermedio",
            "high": "avanzado",
        }
        return ranges.get(range_val, "")

    def _get_dot_color(self, range_val: str) -> str:
        """
        Get dot color for a range
        """
        colors = {
            "low": "red",
            "medium": "yellow",
            "high": "green",
        }
        return colors.get(range_val, "")

    def get(self, request, company_id):
        """
        View to preview the WeasyPrint PDF report using the html-pdf template.
        """

        # Get company and participants
        company = get_object_or_404(models.Company, id=company_id)
        participants = models.Participant.objects.filter(company=company)
        reports = models.Report.objects.filter(participant__in=participants)
        print("reports", reports)
        print("participants", participants)
        print("company", company)

        # Calculate current date in Spanish
        MONTHS_ES = {
            1: "enero",
            2: "febrero",
            3: "marzo",
            4: "abril",
            5: "mayo",
            6: "junio",
            7: "julio",
            8: "agosto",
            9: "septiembre",
            10: "octubre",
            11: "noviembre",
            12: "diciembre",
        }
        now = datetime.now()
        current_date_es = f"{now.day} de {MONTHS_ES[now.month]} {now.year}"

        # Calculate group calcs
        calcs = SurveyCalcsGroupTexts(reports=reports)

        # Prepare nominal ranking raw list and chunks to handle WeasyPrint pagination bug gracefully
        nominal_ranking_raw = [
            {
                "counter": idx + 1,
                "name": report.participant.name,
                "position": report.participant.get_position_display(),
                "score": round(report.total),
                "level": calcs.LEVELS_CONFIG[calcs._get_level_from_score(report.total)][
                    "name_es"
                ],
                "dot_color": calcs.LEVELS_CONFIG[
                    calcs._get_level_from_score(report.total)
                ]["dot_color"],
            }
            for idx, report in enumerate(reports.order_by("-total"))
        ]

        nominal_ranking_chunks = self._chunk_list(
            nominal_ranking_raw, self.NOMINAL_RANKING_CHUNK_SIZE
        )
        heatmap_chunks = self._chunk_list(
            calcs.get_heatmap_data(), self.HEATMAP_CHUNK_SIZE
        )
        strategic_profiles = calcs.get_strategic_profiles()

        # Mock data for all dynamic sections
        context = {
            # Global data
            # --------------------------
            "company_name": company.name,
            "total_participants": calcs.get_employees_number(),
            "dispersion_summary": calcs.get_dispersion_summary(),
            "levels_config": calcs.LEVELS_CONFIG,
            "strength_areas": calcs.get_strength_areas(),
            "weakness_areas": calcs.get_weakness_areas(),
            # --------------------------
            # Data page 1
            # --------------------------
            "report_date": current_date_es,
            # --------------------------
            # Data page 2
            # --------------------------
            # Data page 3
            # --------------------------
            # Paragraph 1
            "average_score": calcs.get_average(),
            "level": self._get_range_es(calcs.get_average_range()),
            "general_summary": calcs.get_general_summary(),
            "priority_summary": calcs.get_priority_summary(),
            # --------------------------
            # Data page 5
            # --------------------------
            "max_score": calcs.get_max_score(),
            "min_score": calcs.get_min_score(),
            # --------------------------
            # Data page 6
            # --------------------------
            "participant_distribution": [
                {
                    "level": self._get_range_es(item["level"]).capitalize(),
                    "count": item["count"],
                    "percentage": item["percentage"],
                    "dot_color": self._get_dot_color(item["level"]),
                }
                for item in calcs.get_participant_distribution()
            ],
            "area_results": [
                {
                    "name": item["display_name"],
                    "score": item["average"],
                }
                for item in calcs.get_average_areas_ordered(use_summary=True)
            ],
            # --------------------------
            # Data page 7
            # --------------------------
            "theme_ranking": [
                {
                    "name": item["area"].name,
                    "score": item["average"],
                }
                for item in calcs.get_average_areas_ordered(use_summary=False)
            ],
            # --------------------------
            # Data page 8
            # --------------------------
            "nominal_ranking": nominal_ranking_raw,
            "nominal_ranking_chunks": nominal_ranking_chunks,
            # --------------------------
            # Data page 9
            # --------------------------
            "heatmap_themes": calcs.get_heatmap_themes(),
            "heatmap_chunks": heatmap_chunks,
            # --------------------------
            # Data page 10
            # --------------------------
            "strategic_profiles": strategic_profiles,
            "strategic_ambassadors_chunks": self._chunk_list(
                strategic_profiles["ambassadors"], self.STRATEGIC_CHUNK_SIZE
            ),
            "strategic_champions_chunks": self._chunk_list(
                strategic_profiles["champions"], self.STRATEGIC_CHUNK_SIZE
            ),
            "strategic_risks_chunks": self._chunk_list(
                strategic_profiles["risks"], self.STRATEGIC_CHUNK_SIZE
            ),
            "strategic_labels": {
                "high_tech": self._get_range_es("high").capitalize(),
                "low_tech": self._get_range_es("low").capitalize(),
                "high_influence": "Alta",
                "medium_low_influence": "Media/Baja",
            },
            # --------------------------
            # Data page 11
            # --------------------------
            "priority_actions": calcs.get_priority_actions(),
            "additional_recommendations": [
                "Establecer un programa de mentoría interna donde los 'Champions' apoyen a otros líderes.",
                "Realizar talleres prácticos trimestrales sobre tecnologías emergentes aplicadas al sector.",
            ],
        }

        # Render HTML string from template
        html_string = render_to_string("survey/pdf/group_report_template.html", context)

        # Base URL for assets resolution
        base_url = os.path.join(
            settings.BASE_DIR, "survey", "templates", "survey", "pdf"
        )

        # Generate PDF via WeasyPrint
        pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = "inline; filename='group_report.pdf'"
        return response


class OptionsView(APIView):
    def get(self, request):
        def format_choices(choices_list):
            return [{"value": c[0], "label": c[1]} for c in choices_list]

        data = {
            "status": choices.STATUS_CHOICES,
            "gender": choices.GENDER_CHOICES,
            "birth_range": choices.BIRTH_RANGE_CHOICES,
            "position": choices.POSITION_CHOICES,
            "department": choices.DEPARTMENT_CHOICES,
        }

        # Format each list
        formatted_data = {key: format_choices(val) for key, val in data.items()}

        return Response(formatted_data, status=status.HTTP_200_OK)


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
        survey_id = request.query_params.get("survey_id")

        if not email or not survey_id:
            return Response(
                {"detail": "email and survey_id parameters are required."},
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
        survey_id = request.data.get("survey_id")

        if not email or not survey_id:
            return Response(
                {"detail": "email and survey_id are required."},
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
        survey_id = request.query_params.get("survey_id")

        if not email or not survey_id:
            return Response(
                {"detail": "email and survey_id parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        models.FormProgress.objects.filter(email=email, survey_id=survey_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
