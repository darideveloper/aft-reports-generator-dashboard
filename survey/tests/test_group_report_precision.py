import pytest
from django.template.loader import render_to_string
from survey.models import Report, Participant, Company, QuestionGroup, Survey, ReportQuestionGroupTotal
from utils.survey_calcs_group import SurveyCalcsGroupTexts

GENDER_CHOICES = [
    ("male", "Masculino"),
    ("female", "Femenino"),
    ("other", "Otro"),
]

BIRTH_RANGE_CHOICES = [
    ("18-25", "18-25"),
    ("26-35", "26-35"),
    ("36-45", "36-45"),
    ("46-55", "46-55"),
    ("56+", "56 o más"),
]

POSITION_CHOICES = [
    ("analista", "Analista"),
    ("coordinador", "Coordinador"),
    ("director", "Director"),
    ("gerente", "Gerente"),
]


@pytest.mark.django_db
def test_group_report_decimal_precision():
    survey = Survey.objects.create(name="Test Survey", instructions="Test")
    qg1 = QuestionGroup.objects.create(survey=survey, name="Cultura digital", survey_index=1, survey_percentage=50)
    qg2 = QuestionGroup.objects.create(survey=survey, name="Tecnología y negocios", survey_index=2, survey_percentage=50)

    company = Company.objects.create(name="Test Company")

    p1 = Participant.objects.create(
        name="User 1", company=company, email="user1@test.com",
        gender="male", birth_range="26-35", position="analista",
    )
    r1 = Report.objects.create(participant=p1, survey=survey, total=85.5, status="completed")
    ReportQuestionGroupTotal.objects.create(report=r1, question_group=qg1, total=80.0)
    ReportQuestionGroupTotal.objects.create(report=r1, question_group=qg2, total=91.0)

    p2 = Participant.objects.create(
        name="User 2", company=company, email="user2@test.com",
        gender="female", birth_range="36-45", position="director",
    )
    r2 = Report.objects.create(participant=p2, survey=survey, total=90.0, status="completed")
    ReportQuestionGroupTotal.objects.create(report=r2, question_group=qg1, total=85.0)
    ReportQuestionGroupTotal.objects.create(report=r2, question_group=qg2, total=95.0)

    reports = Report.objects.filter(id__in=[r1.id, r2.id])
    calcs = SurveyCalcsGroupTexts(reports=reports)

    nominal_ranking_raw = [
        {
            "counter": idx + 1,
            "name": report.participant.name,
            "position": report.participant.get_position_display(),
            "score": report.total,
            "level": calcs.LEVELS_CONFIG[calcs._get_level_from_score(report.total)][
                "name_es"
            ],
            "dot_color": calcs.LEVELS_CONFIG[calcs._get_level_from_score(report.total)][
                "dot_color"
            ],
        }
        for idx, report in enumerate(reports.order_by("-total"))
    ]

    context = {
        "company_name": company.name,
        "total_participants": calcs.get_employees_number(),
        "dispersion_summary": calcs.get_dispersion_summary(),
        "levels_config": calcs.LEVELS_CONFIG,
        "strength_areas": calcs.get_strength_areas(),
        "weakness_areas": calcs.get_weakness_areas(),
        "report_date": "27 de mayo 2026",
        "average_score": calcs.get_average(),
        "level": "Avanzado",
        "general_summary": calcs.get_general_summary(),
        "priority_summary": calcs.get_priority_summary(),
        "max_score": calcs.get_max_score(),
        "min_score": calcs.get_min_score(),
        "participant_distribution": [
            {
                "level": "Avanzado",
                "count": 2,
                "percentage": 100.0,
                "dot_color": "green",
            }
        ],
        "area_results": [
            {"name": "Area 1", "score": 87.75}
        ],
        "theme_ranking": [
            {"name": "Tema 1", "score": 87.75}
        ],
        "nominal_ranking": nominal_ranking_raw,
        "nominal_ranking_chunks": [nominal_ranking_raw],
        "heatmap_themes": calcs.get_heatmap_themes(),
        "heatmap_chunks": [],
        "strategic_profiles": calcs.get_strategic_profiles(),
        "strategic_ambassadors_chunks": [],
        "strategic_champions_chunks": [],
        "strategic_risks_chunks": [],
        "strategic_labels": {
            "high_tech": "Avanzado",
            "low_tech": "Basico",
            "high_influence": "Alta",
            "medium_low_influence": "Media/Baja",
        },
        "weakness_question_groups": calcs.get_weakness_areas(summary=False),
        "priority_actions": calcs.get_priority_actions(),
        "additional_recommendations": [],
    }

    html_string = render_to_string("survey/pdf/group_report_template.html", context)

    assert "85.50" in html_string
    assert "90.00" in html_string
    assert "87.75" in html_string
    assert "User 1" in html_string
    assert "User 2" in html_string
    assert "0.00 \u2013 59.00" in html_string
    assert "60.00 \u2013 79.00" in html_string
    assert "80.00 \u2013 100.00" in html_string
