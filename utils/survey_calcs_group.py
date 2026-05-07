from survey import models


class SurveyCalcsGroup:

    def __init__(
        self,
        reports: list[models.Report],
    ):
        self.reports = reports

    def get_employees_number(self) -> int:
        """
        Get the number of employees in the company

        Returns:
            int: Number of employees
        """
        return len(self.reports)
