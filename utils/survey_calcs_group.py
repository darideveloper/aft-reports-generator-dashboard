from django.db.models import QuerySet

from survey import models

from django.db.models import Avg
from django.db.models import StdDev


class SurveyCalcsGroup:

    def __init__(
        self,
        reports: QuerySet[models.Report],
    ):
        self.reports = reports

    def get_employees_number(self) -> int:
        """
        Get the number of employees in the company

        Returns:
            int: Number of employees
        """
        return self.reports.count() or 1

    def get_average_num(self) -> float:
        """
        Get the average number of employees in the company

        Returns:
            float: Average number of employees
        """

        return round(
            (
                sum(report.total for report in self.reports)
                / self.get_employees_number()
            ),
            2,
        )

    def get_average_range(self) -> str:
        """
        Get the average range of the employees in the company (low / medium / high)

        Returns:
            str: Average range label
        """

        average = self.get_average_num()

        if average <= 59:
            return "bajo"
        elif average <= 79:
            return "medio"
        else:
            return "alto"

    def get_general_summary(self) -> str:
        """
        Get a general summary description based on the average range.

        Returns:
            str: General summary paragraph.
        """
        summaries = {
            "bajo": "Este resultado sugiere que el grupo se encuentra en una fase inicial de adopción tecnológica. Existen importantes oportunidades para desarrollar las habilidades digitales fundamentales y fomentar una cultura de innovación.",
            "medio": "Este resultado sugiere que los participantes cuentan con una base tecnológica funcional que les permite utilizar herramientas digitales en su trabajo diario. Sin embargo, aún existen oportunidades para fortalecer la comprensión de temas tecnológicos estratégicos.",
            "alto": "Este resultado sugiere que el grupo posee un dominio avanzado de las herramientas tecnológicas y una sólida comprensión de las tendencias digitales. Están bien posicionados para liderar iniciativas de transformación digital dentro de la organización.",
        }

        return summaries.get(self.get_average_range(), "")

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
        from django.db.models import Avg
        from survey.models import (
            ReportQuestionGroupTotal,
            ReportSummaryScore,
            QuestionGroup,
            TextPDFSummary,
        )

        if not self.reports.exists():
            return []

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
            return final_results
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
            qgs = {qg.id: qg for qg in QuestionGroup.objects.filter(id__in=qg_ids)}

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
            return final_results

    def get_average_question_groups_ordered(self) -> dict[str, float]:
        """
        Get the average of each area in the company ordered by average (from highest to lowest)

        Returns:
            dict[str, float]: Average of each area ordered by average
        """
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
            question_group_total_avg = question_group_totals.aggregate(Avg("total"))[
                "total__avg"
            ]
            area_averages[question_group.name] = question_group_total_avg

        # Order by average
        return dict(reversed(sorted(area_averages.items(), key=lambda item: item[1])))

    def get_standard_deviation_total(self) -> float:
        """
        Get the standard deviation of the total of the reports in the company

        Returns:
            float: Standard deviation of the total of the reports
        """
        # Naming it 'std_dev' explicitly makes the dictionary lookup cleaner
        result = self.reports.aggregate(std_dev=StdDev("total"))
        return result["std_dev"] or 0.0

    def get_standard_deviation_total_range(self) -> str:
        """
        Get the standard deviation range of the total of the reports in the company (baja / media / alta)

        Returns:
            str: Standard deviation range label
        """

        standard_deviation = round(self.get_standard_deviation_total(), 1)

        if standard_deviation <= 8:
            return "baja"
        elif standard_deviation <= 15:
            return "media"
        else:
            return "alta"


