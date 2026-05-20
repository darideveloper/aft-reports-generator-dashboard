import os
import random
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from weasyprint import HTML

from core import choices
from survey import models, serializers


def preview_pdf_sample(request):
    """
    View to preview the WeasyPrint PDF sample in the browser.
    """
    # Generate random data for the template
    rows = []
    statuses = ["Active", "Pending", "Completed", "Failed"]
    for i in range(1, 150):
        rows.append(
            {
                "id": i,
                "name": f"Item {i}",
                "value1": round(random.uniform(10.0, 999.9), 2),
                "value2": random.randint(1, 100),
                "status": random.choice(statuses),
            }
        )

    # Pick a random primary color for the sample
    primary_color = "#2c3e50"

    # Resolve logo URL if exists
    logo_url = None
    if os.path.exists(os.path.join(settings.BASE_DIR, "media", "logo.png")):
        logo_url = request.build_absolute_uri(settings.MEDIA_URL + "logo.png")

    context = {
        "title": "WeasyPrint Sample Report (Live Preview)",
        "subtitle": "Demonstrating Paged Media CSS in Django",
        "year": datetime.now().year,
        "date": datetime.now().strftime("%B %d, %Y"),
        "rows": rows,
        "primary_color": primary_color,
        "logo_url": logo_url,
    }

    # Render HTML string from template
    html_string = render_to_string("survey/group_report.html", context)

    # Generate PDF via WeasyPrint
    base_url = request.build_absolute_uri("/")
    pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename='preview.pdf'"
    return response


def preview_report_pdf(request):
    """
    View to preview the WeasyPrint PDF report using the html-pdf template.
    """
    # Mock data for all dynamic sections
    context = {
        "company_name": "Acme Corp (Dynamic Preview)",
        "total_participants": 42,
        "report_date": "13 de mayo 2026",
        "average_score": 67,
        "max_score": 91,
        "min_score": 43,
        "level": "Intermedio",
        "summary_paragraphs": [
            "Este resultado sugiere que los participantes cuentan con una base tecnológica funcional que les permite utilizar herramientas digitales en su trabajo diario. Sin embargo, aún existen oportunidades para fortalecer la comprensión de temas tecnológicos estratégicos.",
            "Las principales fortalezas del grupo se observan en las áreas de <strong>Ecosistema digital de colaboración</strong> y <strong>Cultura digital</strong>, lo que indica que los líderes han desarrollado capacidades relevantes en estos ámbitos tecnológicos.",
            "Las principales áreas de oportunidad se concentran en <strong>Ciberseguridad</strong> y <strong>Tecnología y negocios</strong>, lo que sugiere la necesidad de fortalecer la comprensión de riesgos y consolidar el dominio en estos temas.",
            "Los resultados muestran diferencias moderadas entre participantes, lo que indica que el nivel de alfabetización tecnológica no es completamente homogéneo dentro del grupo. Esto puede generar distintas velocidades de adopción tecnológica dentro de la organización.",
            "Observar la variabilidad entre los participantes permite identificar tanto posibles focos de riesgo como líderes que pueden actuar como aliados de la transformación digital.",
            "Resulta prioritario fortalecer la comprensión de cómo las decisiones tecnológicas impactan en el negocio considerando también los riesgos asociados a la seguridad de la información. Esto permitirá evaluar con mayor criterio iniciativas y reducir vulnerabilidades operativas."
        ],
        "global_index_interpretation": "Los resultados muestran diferencias moderadas entre participantes, lo que indica que el nivel de alfabetización tecnológica no es completamente homogéneo dentro del grupo. Esto puede generar distintas velocidades de adopción tecnológica dentro de la organización.",
        "participant_distribution": [
            {"level": "Avanzado", "count": 5, "percentage": 12, "dot_color": "green"},
            {"level": "Intermedio", "count": 26, "percentage": 62, "dot_color": "yellow"},
            {"level": "Básico", "count": 11, "percentage": 26, "dot_color": "red"},
        ],
        "area_results": [
            {"name": "Ecosistema digital de colaboración", "score": 74},
            {"name": "Cultura digital", "score": 72},
            {"name": "Impacto personal", "score": 69},
            {"name": "Futuro sustentable e inclusivo", "score": 64},
            {"name": "Tecnología y negocios", "score": 61},
            {"name": "Ciberseguridad", "score": 58},
        ],
        "theme_ranking": [
            {"name": "Herramientas de colaboración", "score": 76},
            {"name": "Uso de la tecnología", "score": 74},
            {"name": "Internet y conectividad", "score": 72},
            {"name": "Etiqueta digital", "score": 71},
            {"name": "Dispositivos digitales", "score": 69},
            {"name": "Tecnologías de asistencia", "score": 66},
            {"name": "Huella digital", "score": 63},
            {"name": "Rol del líder y la tecnología", "score": 62},
            {"name": "Tecnologías emergentes", "score": 60},
            {"name": "Tecnología y medio ambiente", "score": 59},
            {"name": "Evolución de la tecnología", "score": 58},
            {"name": "Ciberseguridad", "score": 55},
            {"name": "Antecedentes tecnológicos", "score": 52},
        ],
        "nominal_ranking": [
            {"name": "Laura Isabel Martínez Hinojosa", "position": "Director", "score": 89, "level": "Avanzado", "dot_color": "green"},
            {"name": "Carlos Enrique Gómez Martínez", "position": "Gerente", "score": 85, "level": "Avanzado", "dot_color": "green"},
            {"name": "Ana María Torres de la Garza", "position": "Jefe de Departamento", "score": 77, "level": "Intermedio", "dot_color": "yellow"},
            {"name": "Luis Alfonso Herrera Barrera", "position": "Gerente", "score": 72, "level": "Intermedio", "dot_color": "yellow"},
            {"name": "Mariana de Jesús Ríos González", "position": "Coordinadora", "score": 68, "level": "Intermedio", "dot_color": "yellow"},
            {"name": "Javier Ignacio López García", "position": "Supervisor", "score": 59, "level": "Básico", "dot_color": "red"},
            {"name": "Patricia del Rocío Núñez Jimenez", "position": "Gerente", "score": 54, "level": "Básico", "dot_color": "red"},
            {"name": "Ricardo Díaz Sánchez-Cordero", "position": "Director", "score": 51, "level": "Básico", "dot_color": "red"},
        ],
        "heatmap_themes": [
            "Antecedentes tecnológicos", "Evolución de la tecnología", "Internet y conectividad",
            "Dispositivos digitales", "Ciberseguridad", "Huella digital", "Uso de la tecnología",
            "Herramientas de colaboración", "Tecnologías emergentes", "Tecnologías de asistencia",
            "Rol del líder y la tecnología", "Tecnología y medio ambiente", "Etiqueta digital"
        ],
        "heatmap_data": [
            {"name": "Laura Isabel Martínez Hinojosa", "dots": ["green", "green", "green", "green", "green", "green", "green", "green", "green", "green", "green", "yellow", "green"]},
            {"name": "Carlos Enrique Gómez Martínez", "dots": ["yellow", "yellow", "green", "yellow", "yellow", "yellow", "green", "green", "yellow", "yellow", "green", "yellow", "green"]},
            {"name": "Ana María Torres de la Garza", "dots": ["yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "yellow", "green", "yellow", "yellow", "yellow", "yellow", "green"]},
        ],
        "strategic_profiles": {
            "ambassadors": [],
            "champions": ["Carlos Enrique Gómez Martínez", "Ana María Torres de la Garza", "Luis Alfonso Herrera Barrera"],
            "risks": ["Ricardo Díaz López", "Mariana Ríos González"]
        },
        "priority_actions": [
            {
                "title": "Antecedentes tecnológicos",
                "items": [
                    "Reforzar conceptos básicos sobre cómo funciona la tecnología y su evolución en el negocio.",
                    "Integrar fundamentos tecnológicos en sesiones de inducción o actualización interna.",
                    "Relacionar conceptos tecnológicos con casos prácticos del entorno organizacional."
                ]
            },
            {
                "title": "Ciberseguridad",
                "items": [
                    "Implementar lineamientos básicos de seguridad digital para toda la organización.",
                    "Sensibilizar sobre riesgos comunes como phishing, accesos indebidos y manejo de información.",
                    "Integrar prácticas de seguridad en el uso cotidiano de herramientas digitales."
                ]
            }
        ],
        "additional_recommendations": [
            "Establecer un programa de mentoría interna donde los 'Champions' apoyen a otros líderes.",
            "Realizar talleres prácticos trimestrales sobre tecnologías emergentes aplicadas al sector."
        ]
    }

    # Render HTML string from template
    html_string = render_to_string("survey/pdf/report_template.html", context)

    # Base URL for assets resolution
    base_url = os.path.join(settings.BASE_DIR, "survey", "templates", "survey", "pdf")

    # Generate PDF via WeasyPrint
    pdf_bytes = HTML(string=html_string, base_url=base_url).write_pdf()

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename='preview_report.pdf'"
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
