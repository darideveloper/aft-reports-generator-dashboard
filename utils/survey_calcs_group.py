from django.db.models import QuerySet

from survey import models


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

        return (
            sum(report.total for report in self.reports) / self.get_employees_number()
        )

    def get_average_range(self) -> str:
        """
        Get the average range of the employees in the company (low / medium / high)

        Returns:
            str: Average range label
        """

        average = self.get_average_num()

        if average <= 59:
            return "low"
        elif average <= 79:
            return "medium"
        else:
            return "high"

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
                display_name = dict(TextPDFSummary.TEXT_TYPE_CHOICES).get(p_type, p_type)
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
