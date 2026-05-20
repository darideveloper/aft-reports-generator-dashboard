from django.db.models import Avg, Max, Min, QuerySet, StdDev

from survey import models
from survey.models import (
    QuestionGroup,
    ReportQuestionGroupTotal,
    ReportSummaryScore,
    TextPDFSummary,
)


class SurveyCalcsGroup:
    # Centralized definition of assessment levels, scores, colors, and descriptions
    LEVELS_CONFIG = {
        "low": {
            "name_es": "Básico",
            "dot_color": "red",
            "score_min": 0,
            "score_max": 59.99,
            "score_max_display": 59,
            "description": "Conocimiento limitado"
        },
        "medium": {
            "name_es": "Intermedio",
            "dot_color": "yellow",
            "score_min": 60,
            "score_max": 79.99,
            "score_max_display": 79,
            "description": "Conocimiento funcional"
        },
        "high": {
            "name_es": "Avanzado",
            "dot_color": "green",
            "score_min": 80,
            "score_max": 100,
            "score_max_display": 100,
            "description": "Dominio sólido"
        }
    }

    def __init__(
        self,
        reports: QuerySet[models.Report],
    ):
        self.reports = reports
        self._employees_number = None
        self._average = None
        self._average_areas_ordered = {}  # {use_summary: result}
        self._average_question_groups_ordered = None
        self._standard_deviation_total = None
        self._max_score = None
        self._min_score = None
        self._participant_distribution = None
        self._heatmap_themes = None
        self._heatmap_data = None

    def get_employees_number(self) -> int:
        """
        Get the number of employees in the company

        Returns:
            int: Number of employees
        """
        if self._employees_number is None:
            self._employees_number = self.reports.count() or 1
        return self._employees_number

    def get_average(self) -> float:
        """
        Get the average number of employees in the company

        Returns:
            float: Average number of employees
        """
        if self._average is None:
            self._average = round(
                (
                    sum(report.total for report in self.reports)
                    / self.get_employees_number()
                ),
                2,
            )
        return self._average

    def get_average_areas_ordered(self, use_summary: bool = False) -> list[dict]:
        """
        Get the average for each area (QuestionGroup or Summary Category),
        sorted from highest to lowest average.

        Args:
            use_summary (bool): If True, aggregate by ReportSummaryScore instead of QuestionGroup

        Returns:
            list[dict]: List of areas and their averages, e.g.:
                [{"area": <instance>, "average": 85.5}, ...]
        """
        if use_summary not in self._average_areas_ordered:
            if not self.reports.exists():
                self._average_areas_ordered[use_summary] = []
            else:
                if use_summary:
                    # Aggregate by summary category (paragraph_type)
                    results = (
                        ReportSummaryScore.objects.filter(report__in=self.reports)
                        .values("paragraph_type")
                        .annotate(average=Avg("score"))
                        .order_by("-average")
                    )

                    # Map results to include descriptive info (using one match for paragraph_type)
                    final_results = []
                    for item in results:
                        p_type = item["paragraph_type"]
                        # We can't return a single 'instance' for paragraph_type as it's a choice field,
                        # but we can return the display name and perhaps a representative TextPDFSummary
                        display_name = dict(TextPDFSummary.TEXT_TYPE_CHOICES).get(
                            p_type, p_type
                        )
                        final_results.append(
                            {
                                "area": p_type,
                                "display_name": display_name,
                                "average": round(item["average"], 2),
                            }
                        )
                    self._average_areas_ordered[use_summary] = final_results
                else:
                    # Aggregate by QuestionGroup
                    results = (
                        ReportQuestionGroupTotal.objects.filter(report__in=self.reports)
                        .values("question_group")
                        .annotate(average=Avg("total"))
                        .order_by("-average")
                    )

                    # Map IDs back to QuestionGroup instances
                    qg_ids = [item["question_group"] for item in results]
                    qgs = {
                        qg.id: qg for qg in QuestionGroup.objects.filter(id__in=qg_ids)
                    }

                    final_results = []
                    for item in results:
                        qg = qgs.get(item["question_group"])
                        if qg:
                            final_results.append(
                                {
                                    "area": qg,
                                    "average": round(item["average"], 2),
                                }
                            )
                    self._average_areas_ordered[use_summary] = final_results

        print(self._average_areas_ordered[use_summary])
        return self._average_areas_ordered[use_summary]

    def get_average_question_groups_ordered(self) -> dict[str, float]:
        """
        Get the average of each area in the company ordered by average (from highest to lowest)

        Returns:
            dict[str, float]: Average of each area ordered by average
        """
        if self._average_question_groups_ordered is None:
            # Initialize dictionary to store average areas
            area_averages = {}

            # Get all areas
            question_groups = models.QuestionGroup.objects.all()

            # Calculate average for each question group
            for question_group in question_groups:
                question_group_totals = models.ReportQuestionGroupTotal.objects.filter(
                    question_group=question_group,
                    report__in=self.reports,
                )
                question_group_total_avg = question_group_totals.aggregate(
                    Avg("total")
                )["total__avg"]
                area_averages[question_group.name] = question_group_total_avg

            # Order by average
            self._average_question_groups_ordered = dict(
                reversed(sorted(area_averages.items(), key=lambda item: item[1]))
            )

        return self._average_question_groups_ordered

    def get_standard_deviation_total(self) -> float:
        """
        Get the standard deviation of the total of the reports in the company

        Returns:
            float: Standard deviation of the total of the reports
        """
        if self._standard_deviation_total is None:
            # Naming it 'std_dev' explicitly makes the dictionary lookup cleaner
            result = self.reports.aggregate(std_dev=StdDev("total"))
            self._standard_deviation_total = round(result["std_dev"] or 0.0, 2)
        return self._standard_deviation_total

    def get_max_score(self) -> float:
        """
        Get the maximum score among the reports in the company

        Returns:
            float: Maximum score
        """
        if self._max_score is None:
            if not self.reports.exists():
                self._max_score = 0.0
            else:
                result = self.reports.aggregate(max_score=Max("total"))
                self._max_score = round(result["max_score"] or 0.0, 2)
        return self._max_score

    def get_min_score(self) -> float:
        """
        Get the minimum score among the reports in the company

        Returns:
            float: Minimum score
        """
        if self._min_score is None:
            if not self.reports.exists():
                self._min_score = 0.0
            else:
                result = self.reports.aggregate(min_score=Min("total"))
                self._min_score = round(result["min_score"] or 0.0, 2)
        return self._min_score

    def _get_level_from_score(self, score: float) -> str:
        """
        Helper method to map a score to low, medium, or high range.
        """
        for level_key, config in self.LEVELS_CONFIG.items():
            if config["score_min"] <= score <= config["score_max"]:
                return level_key
        return "low"

    def get_participant_distribution(self) -> list[dict]:
        """
        Get the distribution of participants across basic, intermediate, and advanced levels.

        Returns:
            list[dict]: Array of objects containing level, count, and percentage.
        """
        if self._participant_distribution is None:
            advanced_count = 0
            intermediate_count = 0
            basic_count = 0

            for report in self.reports:
                lvl = self._get_level_from_score(report.total)
                if lvl == "high":
                    advanced_count += 1
                elif lvl == "medium":
                    intermediate_count += 1
                else:
                    basic_count += 1

            total_reports = self.reports.count()
            if total_reports > 0:
                advanced_pct = round((advanced_count / total_reports) * 100, 2)
                intermediate_pct = round((intermediate_count / total_reports) * 100, 2)
                basic_pct = round(100.0 - advanced_pct - intermediate_pct, 2)
            else:
                advanced_pct = 0.0
                intermediate_pct = 0.0
                basic_pct = 0.0

            self._participant_distribution = [
                {
                    "level": "high",
                    "count": advanced_count,
                    "percentage": advanced_pct,
                },
                {
                    "level": "medium",
                    "count": intermediate_count,
                    "percentage": intermediate_pct,
                },
                {
                    "level": "low",
                    "count": basic_count,
                    "percentage": basic_pct,
                },
            ]
        return self._participant_distribution

    def clean_theme_name(self, name: str) -> str:
        """
        Strip prefix from theme name
        """
        if " - " in name:
            return name.split(" - ", 1)[1].strip()
        return name

    def get_heatmap_themes(self) -> list[str]:
        """
        Get the list of cleaned theme names for the survey.
        """
        if self._heatmap_themes is None:
            survey = self.reports.first().survey if self.reports.exists() else None
            if survey:
                question_groups = QuestionGroup.objects.filter(survey=survey).order_by("survey_index")
            else:
                question_groups = QuestionGroup.objects.none()
            self._heatmap_themes = [self.clean_theme_name(qg.name) for qg in question_groups]
        return self._heatmap_themes

    def get_heatmap_data(self) -> list[dict]:
        """
        Get the heatmap data (dots and names) for the participants.
        """
        if self._heatmap_data is None:
            survey = self.reports.first().survey if self.reports.exists() else None
            if survey:
                question_groups = QuestionGroup.objects.filter(survey=survey).order_by("survey_index")
            else:
                question_groups = QuestionGroup.objects.none()

            self._heatmap_data = []
            for report in self.reports.order_by("-total"):
                group_totals = ReportQuestionGroupTotal.objects.filter(report=report)
                scores_by_group = {gt.question_group_id: gt.total for gt in group_totals}
                
                dots = []
                for qg in question_groups:
                    score = scores_by_group.get(qg.id, 0.0)
                    level_key = self._get_level_from_score(score)
                    dot_color = self.LEVELS_CONFIG[level_key]["dot_color"]
                    dots.append(dot_color)
                    
                self._heatmap_data.append({
                    "name": report.participant.name,
                    "dots": dots,
                })
        return self._heatmap_data

    def get_strategic_profiles(self) -> dict:
        """
        Compute and return the strategic profiles (ambassadors, champions, risks)
        based on participant scores and position influence mapping.
        """
        from core.choices import (
            POSITION_INFLUENCE_MAP,
            INFLUENCE_HIGH,
            INFLUENCE_MEDIUM,
            INFLUENCE_LOW,
        )

        ambassadors = []
        champions = []
        risks = []

        for report in self.reports.order_by("-total"):
            tech_level = self._get_level_from_score(report.total)
            influence_level = POSITION_INFLUENCE_MAP.get(
                report.participant.position, INFLUENCE_LOW
            )

            if tech_level == "high" and influence_level == INFLUENCE_HIGH:
                ambassadors.append(report.participant.name)
            elif tech_level == "high" and influence_level in (
                INFLUENCE_MEDIUM,
                INFLUENCE_LOW,
            ):
                champions.append(report.participant.name)
            elif tech_level == "low" and influence_level == INFLUENCE_HIGH:
                risks.append(report.participant.name)

        return {
            "ambassadors": ambassadors,
            "champions": champions,
            "risks": risks,
        }


class SurveyCalcsGroupTexts(SurveyCalcsGroup):

    def __init__(self, reports: QuerySet[models.Report]):
        super().__init__(reports)
        self._average_range = None
        self._general_summary = None
        self._strength_areas = None
        self._weakness_areas = None
        self._standard_deviation_total_range = None
        self._dispersion_summary = None
        self._priority_summary = None

    def _get_extreme_areas(self, indices: list[int]) -> list[str]:
        """
        Helper method to get display names of areas at specific indices of the ordered list.
        """
        ordered_areas = self.get_average_areas_ordered(use_summary=True)
        if len(ordered_areas) < 2:
            return []

        choices_dict = dict(TextPDFSummary.TEXT_TYPE_CHOICES)
        names = []
        for idx in indices:
            code = ordered_areas[idx]["area"]
            names.append(choices_dict.get(code, code))
        return names

    def get_average_range(self) -> str:
        """
        Get the average range of the employees in the company (low / medium / high)

        Returns:
            str: Average range label
        """
        if self._average_range is None:
            self._average_range = self._get_level_from_score(self.get_average())
        return self._average_range

    def get_general_summary(self) -> str:
        """
        Get a general summary description based on the average range.

        Returns:
            str: General summary paragraph.
        """
        if self._general_summary is None:
            summaries = {
                "low": "Este resultado sugiere que el grupo presenta una base tecnológica limitada, lo que puede dificultar la interacción cotidiana con herramientas digitales. También puede afectar la participación informada en iniciativas tecnológicas dentro de la organización.",
                "medium": "Este resultado sugiere que los participantes cuentan con una base tecnológica funcional que les permite utilizar herramientas digitales en su trabajo diario. Sin embargo, aún existen oportunidades para fortalecer la comprensión de temas tecnológicos estratégicos.",
                "high": "Este resultado indica que el grupo cuenta con una base tecnológica sólida que facilita la adopción de herramientas digitales. Esto permite a los participantes participar con mayor criterio en iniciativas tecnológicas y decisiones relacionadas con innovación.",
            }

            self._general_summary = summaries.get(self.get_average_range(), "")
        return self._general_summary

    def get_strength_areas(self) -> list[str]:
        """
        Get the names of the top 2 summary areas (strengths).

        Returns:
            list[str]: A list of area names.
        """
        if self._strength_areas is None:
            self._strength_areas = self._get_extreme_areas([0, 1])
        return self._strength_areas

    def get_weakness_areas(self) -> list[str]:
        """
        Get the names of the bottom 2 summary areas (weaknesses).

        Returns:
            list[str]: A list of area names.
        """
        if self._weakness_areas is None:
            self._weakness_areas = self._get_extreme_areas([-1, -2])
        return self._weakness_areas

    def get_standard_deviation_total_range(self) -> str:
        """
        Get the standard deviation range of the total of the reports in the company (baja / media / alta)

        Returns:
            str: Standard deviation range label
        """
        if self._standard_deviation_total_range is None:
            standard_deviation = round(self.get_standard_deviation_total(), 2)

            if standard_deviation <= 8:
                self._standard_deviation_total_range = "low"
            elif standard_deviation <= 15:
                self._standard_deviation_total_range = "medium"
            else:
                self._standard_deviation_total_range = "high"
        return self._standard_deviation_total_range

    def get_dispersion_summary(self) -> str:
        """
        Get a dispersion summary description based on the standard deviation range.

        Returns:
            str: Dispersion summary paragraph.
        """
        if self._dispersion_summary is None:
            summaries = {
                "low": "Los resultados muestran un nivel relativamente homogéneo de alfabetización tecnológica entre los participantes evaluados. Esto sugiere que el grupo comparte una base de conocimiento similar en temas tecnológicos.",
                "medium": "Los resultados muestran diferencias moderadas entre participantes, lo que indica que el nivel de alfabetización tecnológica no es completamente homogéneo dentro del grupo. Esto puede generar distintas velocidades de adopción tecnológica dentro de la organización.",
                "high": "Los resultados muestran diferencias importantes entre participantes en su nivel de alfabetización tecnológica. Esta variabilidad puede generar distintos niveles de comprensión tecnológica, riesgos  y decisiones no homogéneas dentro de la organización.",
            }

            self._dispersion_summary = summaries.get(
                self.get_standard_deviation_total_range(), ""
            )
        return self._dispersion_summary

    def get_priority_summary(self) -> str:
        """
        Get a priority summary description based on the two weakness areas.

        Returns:
            str: Priority summary paragraph.
        """
        if self._priority_summary is None:
            weaknesses = self.get_weakness_areas()
            if len(weaknesses) < 2:
                self._priority_summary = (
                    "No se han identificado suficientes áreas de oportunidad para establecer "
                    "una prioridad de intervención específica."
                )
            else:
                name_to_letter = {
                    "Cultura digital": "A",
                    "Tecnología y negocios": "B",
                    "Ciberseguridad": "C",
                    "Impacto personal": "D",
                    "Tecnología y medio ambiente": "E",
                    "Ecosistema digital de colaboración": "F",
                }

                w1_letter = name_to_letter.get(weaknesses[0])
                w2_letter = name_to_letter.get(weaknesses[1])

                if not w1_letter or not w2_letter:
                    self._priority_summary = (
                        "Se debe estructurar un plan de acción conjunto enfocado en mejorar "
                        f"las áreas de '{weaknesses[0]}' y '{weaknesses[1]}'."
                    )
                else:
                    l1, l2 = sorted([w1_letter, w2_letter])

                    summaries = {
                        ("A", "B"): (
                            "Resulta prioritario fortalecer la comprensión de cómo la tecnología impacta "
                            "directamente en los resultados del negocio y en la forma en que se toman decisiones "
                            "operativas. Esto permitirá que los equipos utilicen la tecnología con mayor criterio "
                            "y alineación estratégica."
                        ),
                        ("A", "C"): (
                            "Resulta prioritario fortalecer la cultura digital incorporando prácticas básicas de "
                            "seguridad tecnológica en el uso cotidiano de herramientas y plataformas. Esto permitirá "
                            "reducir riesgos asociados al manejo de información y al uso de entornos digitales."
                        ),
                        ("A", "D"): (
                            "Resulta prioritario fortalecer la cultura digital promoviendo una mayor conciencia "
                            "sobre cómo el uso de la tecnología influye en las prácticas de trabajo. Esto permitirá "
                            "mejorar la adopción y el aprovechamiento de herramientas digitales en el entorno laboral."
                        ),
                        ("A", "E"): (
                            "Resulta prioritario fortalecer la cultura digital incorporando una visión más amplia "
                            "sobre el impacto de la tecnología en sostenibilidad, inclusión y responsabilidad "
                            "organizacional. Esto permitirá utilizar la tecnología de forma más consciente y alineada "
                            "con los retos del entorno."
                        ),
                        ("A", "F"): (
                            "Resulta prioritario fortalecer la cultura digital para aprovechar de forma más efectiva "
                            "las plataformas y herramientas de colaboración disponibles. Esto permitirá mejorar la "
                            "coordinación entre equipos y el flujo de trabajo en entornos digitales."
                        ),
                        ("B", "C"): (
                            "Resulta prioritario fortalecer la comprensión de cómo las decisiones tecnológicas "
                            "impactan en el negocio considerando también los riesgos asociados a la seguridad de "
                            "la información. Esto permitirá evaluar con mayor criterio iniciativas y reducir "
                            "vulnerabilidades operativas."
                        ),
                        ("B", "D"): (
                            "Resulta prioritario fortalecer la comprensión de cómo las decisiones tecnológicas "
                            "impactan en la forma de trabajar de los equipos. Esto permitirá implementar herramientas "
                            "digitales con mayor claridad and mejorar su adopción en la organización."
                        ),
                        ("B", "E"): (
                            "Resulta prioritario fortalecer la comprensión de cómo la tecnología influye en el modelo "
                            "de negocio considerando también criterios de sostenibilidad e impacto organizacional. "
                            "Esto permitirá tomar decisiones tecnológicas con una visión más amplia de largo plazo."
                        ),
                        ("B", "F"): (
                            "Resulta prioritario fortalecer la comprensión de cómo las herramientas digitales pueden "
                            "habilitar procesos de negocio más eficientes. Esto permitirá aprovechar mejor el "
                            "ecosistema tecnológico disponible para mejorar resultados operativos."
                        ),
                        ("C", "D"): (
                            "Resulta prioritario fortalecer la conciencia sobre riesgos tecnológicos y promover "
                            "prácticas responsables en el uso de herramientas digitales. Esto permitirá reducir "
                            "incidentes asociados al manejo de información y al comportamiento digital."
                        ),
                        ("C", "E"): (
                            "Resulta prioritario fortalecer la comprensión de los riesgos tecnológicos incorporando "
                            "criterios de responsabilidad digital y sostenibilidad. Esto permitirá gestionar la "
                            "tecnología considerando sus implicaciones a largo plazo."
                        ),
                        ("C", "F"): (
                            "Resulta prioritario fortalecer prácticas de seguridad en el uso de herramientas de "
                            "colaboración digital. Esto permitirá establecer políticas más robustas y proteger "
                            "mejor la información que circula en plataformas tecnológicas de trabajo."
                        ),
                        ("D", "E"): (
                            "Resulta prioritario fortalecer la comprensión del impacto que el uso de la tecnología "
                            "tiene en las personas y en la evolución del trabajo. Esto permitirá adoptar herramientas "
                            "digitales de manera más consciente y sostenible."
                        ),
                        ("D", "F"): (
                            "Resulta prioritario fortalecer el uso responsable de herramientas de colaboración "
                            "digital considerando su impacto en la dinámica de trabajo de los equipos. Esto "
                            "permitirá mejorar la interacción y coordinación en entornos tecnológicos."
                        ),
                        ("E", "F"): (
                            "Resulta prioritario fortalecer la comprensión del papel que la tecnología puede jugar "
                            "en la sostenibilidad e inclusión dentro de la organización. Esto permitirá aprovechar "
                            "el ecosistema digital para generar impacto positivo en la forma de trabajar."
                        ),
                    }

                    self._priority_summary = summaries.get(
                        (l1, l2),
                        "Se debe estructurar un plan de acción conjunto enfocado en mejorar "
                        f"las áreas de '{weaknesses[0]}' y '{weaknesses[1]}'.",
                    )
        return self._priority_summary
