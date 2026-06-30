import os
from datetime import datetime

from django.conf import settings
from django.db.models import QuerySet
from django.template.loader import render_to_string
from weasyprint import HTML

from survey import models
from utils.survey_calcs_group import SurveyCalcsGroupTexts

NOMINAL_RANKING_CHUNK_SIZE = 15
HEATMAP_CHUNK_SIZE = 15
STRATEGIC_CHUNK_SIZE = 40

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

RANGES_ES = {
    "low": "básico",
    "medium": "intermedio",
    "high": "avanzado",
}

DOT_COLORS = {
    "low": "red",
    "medium": "yellow",
    "high": "green",
}


def _chunk_list(lst: list, chunk_size: int) -> list[list]:
    if not lst:
        return []
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def _get_range_es(range_val: str) -> str:
    return RANGES_ES.get(range_val, "")


def _get_dot_color(range_val: str) -> str:
    return DOT_COLORS.get(range_val, "")


def generate_group_report_pdf(
    reports: QuerySet[models.Report],
    company_name: str = "Reporte Grupal",
    additional_recommendations: str | None = None,
) -> bytes:
    now = datetime.now()
    current_date_es = f"{now.day} de {MONTHS_ES[now.month]} {now.year}"

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

    nominal_ranking_chunks = _chunk_list(
        nominal_ranking_raw, NOMINAL_RANKING_CHUNK_SIZE
    )
    heatmap_chunks = _chunk_list(calcs.get_heatmap_data(), HEATMAP_CHUNK_SIZE)
    strategic_profiles = calcs.get_strategic_profiles()

    context = {
        "company_name": company_name,
        "total_participants": calcs.get_employees_number(),
        "dispersion_summary": calcs.get_dispersion_summary(),
        "levels_config": calcs.LEVELS_CONFIG,
        "strength_areas": calcs.get_strength_areas(),
        "weakness_areas": calcs.get_weakness_areas(),
        "report_date": current_date_es,
        "average_score": calcs.get_average(),
        "level": _get_range_es(calcs.get_average_range()),
        "general_summary": calcs.get_general_summary(),
        "priority_summary": calcs.get_priority_summary(),
        "max_score": calcs.get_max_score(),
        "min_score": calcs.get_min_score(),
        "participant_distribution": [
            {
                "level": _get_range_es(item["level"]).capitalize(),
                "count": item["count"],
                "percentage": item["percentage"],
                "dot_color": _get_dot_color(item["level"]),
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
        "theme_ranking": [
            {
                "name": item["area"].name,
                "score": item["average"],
            }
            for item in calcs.get_average_areas_ordered(use_summary=False)
        ],
        "nominal_ranking": nominal_ranking_raw,
        "nominal_ranking_chunks": nominal_ranking_chunks,
        "heatmap_themes": calcs.get_heatmap_themes(),
        "heatmap_chunks": heatmap_chunks,
        "strategic_profiles": strategic_profiles,
        "strategic_ambassadors_chunks": _chunk_list(
            strategic_profiles["ambassadors"], STRATEGIC_CHUNK_SIZE
        ),
        "strategic_champions_chunks": _chunk_list(
            strategic_profiles["champions"], STRATEGIC_CHUNK_SIZE
        ),
        "strategic_risks_chunks": _chunk_list(
            strategic_profiles["risks"], STRATEGIC_CHUNK_SIZE
        ),
        "strategic_labels": {
            "high_tech": _get_range_es("high").capitalize(),
            "low_tech": _get_range_es("low").capitalize(),
            "high_influence": "Alta",
            "medium_low_influence": "Media/Baja",
        },
        "weakness_question_groups": calcs.get_weakness_areas(summary=False),
        "priority_actions": calcs.get_priority_actions(),
        "additional_recommendations": [
            line.strip()
            for line in (additional_recommendations or "").splitlines()
            if line.strip()
        ],
    }

    html_string = render_to_string("survey/pdf/group_report_template.html", context)

    base_url = os.path.join(settings.BASE_DIR, "survey", "templates", "survey", "pdf")

    return HTML(string=html_string, base_url=base_url).write_pdf()
