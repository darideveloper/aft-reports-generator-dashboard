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
