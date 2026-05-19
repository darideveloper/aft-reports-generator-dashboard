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

    def get_average_question_groups_ordered(self) -> dict[str, float]:
        """
        Get the average of each area in the company ordered by average

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
        Get the standard deviation range of the total of the reports in the company (low / medium / high)

        Returns:
            str: Standard deviation range label
        """

        standard_deviation = round(self.get_standard_deviation_total(), 1)

        if standard_deviation <= 8:
            return "low"
        elif standard_deviation <= 15:
            return "medium"
        else:
            return "high"
